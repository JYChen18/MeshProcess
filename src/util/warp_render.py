import os
import sys

import pyglet

pyglet.options["headless"] = True
import numpy as np
import warp as wp
import warp.render
import torch
import trimesh
from tqdm import tqdm

os.environ["DISPLAY"] = ":98"  # useless?
import cv2

from .util_file import load_json


def create_view_matrix(position, target):
    # position: the position of the camera
    # target: the position of the object
    # return: the view matrix in opengl format
    front = np.array(target) - np.array(position)
    front = front / np.linalg.norm(front)
    while 1:
        up = np.random.rand(3)
        up /= np.linalg.norm(up)
        if np.linalg.norm(np.cross(front, up)) > 0.1:
            break
    up = up - np.dot(up, front) * front
    up = up / np.linalg.norm(up)
    side = np.cross(front, up)
    view_matrix = np.eye(4)
    view_matrix[3, :3] = np.array(position)
    view_matrix[2, :3] = -front
    view_matrix[1, :3] = up
    view_matrix[0, :3] = side
    return torch.tensor(view_matrix)


def fibonacci_sphere(samples=1, radius=1.0, offset=np.array([0, 0, 0])):
    # return: a list of points on the sphere with the center at offset and the radius of radius
    points = []
    phi = np.pi * (3.0 - np.sqrt(5.0))  # golden angle in radians
    for i in range(samples):
        theta = phi * i  # golden angle increment
        x = np.cos(theta)
        y = np.sin(theta)
        z = 0.1 * np.random.random() / radius
        points.append(
            np.array([x, y, z]) * (radius + 0.1 * np.random.random() - 0.05) + offset
        )
    return points


class WarpRender:
    def __init__(
        self,
        device,
        tile_width=1280,
        tile_height=720,
        z_near=0.1,
        z_far=10.0,
        n_cols=2,
        n_rows=2,
        radius=0.8,
        camera_type="kinect",
    ):
        # tile width and height: the size of each tile
        # n_cols and n_rows: the number of columns and rows
        # screnn_width=tile_width*n_cols, screen_height=tile_height*n_rows
        self.radius = radius
        self.device = device

        self.ncols = n_cols
        self.nrows = n_rows
        self.num_tiles = n_cols * n_rows
        self.tile_width = tile_width
        self.tile_height = tile_height

        self.renderer = wp.render.OpenGLRenderer(
            draw_axis=False,
            draw_grid=False,
            show_info=False,
            draw_sky=False,
            screen_width=tile_width * n_cols,
            screen_height=tile_height * n_rows,
            near_plane=z_near,
            far_plane=z_far,
            vsync=False,
            headless=True,
        )

        # setup intrinsics
        self.cx = tile_width // 2
        self.cy = tile_height // 2

        if camera_type == "kinect":
            self.fx = 608.6939697265625
            self.fy = 608.6422119140625
        else:
            raise NotImplementedError

        self.projection_matrixs = [
            np.array(
                [
                    [2 * self.fx / tile_width, 0, 0, 0],
                    [0, 2 * self.fy / tile_height, 0, 0],
                    [0, 0, -(z_far + z_near) / (z_far - z_near), -1],
                    [0, 0, -2 * z_far * z_near / (z_far - z_near), 0],
                ]
            )
        ] * self.num_tiles

        self.setup_tile_flag = False
        self.help_yy, self.help_xx = torch.meshgrid(
            torch.arange(self.tile_height).to(self.device),
            torch.arange(self.tile_width).to(self.device),
            indexing="ij",
        )
        self.help_xx = self.help_xx[None, :, :, None]
        self.help_yy = self.help_yy[None, :, :, None]
        return

    def update_tile_poses(self, obj_trans):
        camera_positions = fibonacci_sphere(
            self.num_tiles, radius=self.radius, offset=np.array([0, 0, self.radius])
        )
        view_matrix = [
            create_view_matrix(camera_positions[i], obj_trans)
            for i in range(self.num_tiles)
        ]
        self.view_matrix = torch.stack(view_matrix).to(self.device).float()
        inv_view_matrix = torch.inverse(self.view_matrix).tolist()

        if not self.setup_tile_flag:
            self.renderer.setup_tiled_rendering(
                instances=[[0]] * self.num_tiles,
                tile_sizes=[(self.tile_width, self.tile_height)] * self.num_tiles,
                projection_matrices=self.projection_matrixs,
                view_matrices=inv_view_matrix,
                tile_ncols=self.ncols,
                tile_nrows=self.nrows,
            )
            self.setup_tile_flag = True
        else:
            for id in range(self.num_tiles):
                self.renderer.update_tile(
                    tile_id=id,
                    instances=[0],
                    tile_size=(self.tile_width, self.tile_height),
                    projection_matrix=self.projection_matrixs[id],
                    view_matrix=inv_view_matrix[id],
                )
        return

    def get_image(self, mode="depth"):
        if mode == "depth":
            image = wp.zeros(
                (self.num_tiles, self.tile_height, self.tile_width, 1), dtype=wp.float32
            )
        elif mode == "rgb":
            image = wp.zeros(
                (self.num_tiles, self.tile_height, self.tile_width, 3), dtype=wp.float32
            )
        else:
            raise NotImplementedError

        self.renderer.get_pixels(image, split_up_tiles=True, mode=mode)

        return wp.to_torch(image)

    def render(self, obj_mesh, obj_scale, obj_trans, obj_rot):
        self.renderer.clear()
        self.update_tile_poses(obj_trans)
        time = self.renderer.clock_time
        self.renderer.begin_frame(time)
        self.renderer.render_mesh(
            name="mesh",
            points=obj_mesh.vertices,
            indices=obj_mesh.faces,
            pos=obj_trans,
            scale=obj_scale,
            rot=obj_rot,
        )
        self.renderer.end_frame()
        return self.view_matrix

    def depth_to_point_cloud(self, depth_image):
        x = (self.help_xx - self.cx) * depth_image / self.fx
        y = -(self.help_yy - self.cy) * depth_image / self.fy
        camera_coords = torch.cat(
            [x, y, -depth_image, torch.ones_like(x, device=x.device)], axis=-1
        )
        world_coords = (
            camera_coords.view(depth_image.shape[0], -1, 4) @ self.view_matrix
        )
        return world_coords[..., :3]


def batch_warp_render(configs, obj_lst, gpu_id):
    func_config = configs.func
    device = f"cuda:{gpu_id}"
    with wp.ScopedDevice(device):
        renderer = WarpRender(device)

        for obj_code in tqdm(obj_lst):
            obj_mesh = trimesh.load(func_config.input_mesh_path.replace("**", obj_code))
            table_pose_anno = load_json(
                func_config.input_pose_path.replace("**", obj_code)
            )
            output_folder = func_config.save_path.replace("**", obj_code)
            os.makedirs(output_folder, exist_ok=True)
            np.save(
                os.path.join(output_folder, "cam_in.npy"),
                renderer.projection_matrixs[0],
            )

            for scale in func_config.obj_scale_lst:
                obj_scale_path = os.path.join(
                    output_folder, f"scale{str(int(scale*100)).zfill(3)}"
                )

                for pose_num, pose in enumerate(table_pose_anno):
                    batch = renderer.num_tiles
                    obj_pose_path = os.path.join(
                        obj_scale_path, f"pose{str(pose_num).zfill(3)}"
                    )

                    # check path
                    if configs.skip:
                        conti_flag = True
                        for b in range(batch):
                            pc_path = os.path.join(
                                obj_pose_path, f"partial_pc_{str(b).zfill(2)}.npy"
                            )
                            if not os.path.exists(pc_path):
                                conti_flag = False
                                break
                            else:
                                check_pc = np.load(pc_path, allow_pickle=True)
                                if len(check_pc) == 0:
                                    conti_flag = False
                        if conti_flag:
                            continue

                    obj_scale = np.array([scale, scale, scale])
                    obj_trans = np.array(pose[:3]) * scale
                    obj_rot = np.array(pose)[[4, 5, 6, 3]]

                    view_matrix = renderer.render(
                        obj_mesh, obj_scale, obj_trans, obj_rot
                    )

                    if func_config.save_rgb:
                        rgb_image = renderer.get_image(mode="rgb")

                    if func_config.save_depth or func_config.save_pc:
                        depth_image = renderer.get_image(mode="depth")
                        if func_config.save_pc:
                            all_pc = renderer.depth_to_point_cloud(depth_image)
                            mask = depth_image.reshape(batch, -1) < 5

                    # save informations
                    for b in range(batch):
                        os.makedirs(obj_pose_path, exist_ok=True)
                        data_id = str(b).zfill(2)
                        np.save(
                            os.path.join(obj_pose_path, f"cam_ex_{data_id}.npy"),
                            view_matrix[b].cpu().numpy(),
                        )
                        if func_config.save_rgb:
                            cv2.imwrite(
                                os.path.join(obj_pose_path, f"rgb_{data_id}.png"),
                                rgb_image[b].cpu().numpy() * 255,
                            )
                        if func_config.save_depth:
                            cv2.imwrite(
                                os.path.join(obj_pose_path, f"depth_{data_id}.png"),
                                depth_image[b].cpu().numpy(),
                            )
                        if func_config.save_pc:
                            pc = all_pc[b, mask[b]]
                            np.save(
                                os.path.join(
                                    obj_pose_path, f"partial_pc_{data_id}.npy"
                                ),
                                pc.cpu().numpy().astype(np.float16),
                            )
