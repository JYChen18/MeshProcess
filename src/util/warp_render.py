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

from .rotation import np_normalize


def camera_spherical(sample_num, radius=1.0):
    points = np.random.randn(sample_num, 3)
    points = radius * np_normalize(points)
    return points


def camera_circular_zaxis(sample_num, radius=0.8, center=np.array([0, 0, 0.8])):
    phi = np.pi * (3.0 - np.sqrt(5.0))  # golden angle in radians
    theta = np.arange(sample_num) * phi
    pos = center + radius * np.stack([np.cos(theta), np.sin(theta), theta * 0], axis=-1)
    return pos


def camera_view_matrix(
    sample_num,
    pos,
    pos_noise=0,
    lookat=np.array([0, 0, 0.0]),
    lookat_noise=0,
    up=None,
    up_noise=0,
    **kwargs,
):
    pos = pos + pos_noise * (np.random.random((sample_num, 3)) - 0.5)
    lookat = lookat + lookat_noise * (np.random.random((sample_num, 3)) - 0.5)
    front = np_normalize(lookat - pos)

    while 1:
        up = up if up is not None else np.random.randn(sample_num, 3)
        up = np_normalize(up + up_noise * (np.random.random((sample_num, 3)) - 0.5))
        up = up - np.sum(up * front, axis=-1, keepdims=True) * front
        up = np_normalize(up)
        if not np.any(np.linalg.norm(up, axis=-1) < 1e-6):
            break

    view_matrix = np.zeros((sample_num, 4, 4))
    view_matrix[:, 0, :3] = np.cross(front, up)
    view_matrix[:, 1, :3] = up
    view_matrix[:, 2, :3] = -front
    view_matrix[:, 3, :3] = pos
    view_matrix[:, 3, 3] = 1
    return view_matrix


def get_camera_matrix(config):
    if config["type"] == "spherical":
        pos = camera_spherical(config["sample_num"], config["radius"])
    elif config["type"] == "circular_zaxis":
        pos = camera_circular_zaxis(
            config["sample_num"], config["radius"], config["center"]
        )
    else:
        raise NotImplementedError("Unsupported camera type")
    return camera_view_matrix(pos=pos, **config)


def scene_cfg2mesh(scene_cfg, scene_cfg_path):
    tm_lst = []
    for obj in scene_cfg["scene"].values():
        if obj["type"] == "rigid_object":
            tm = trimesh.load(
                os.path.join(os.path.dirname(scene_cfg_path), obj["file_path"]),
                force="mesh",
            )
            tm.vertices *= obj["scale"]
        elif obj["type"] == "plane":
            continue
            plane_thick = 0.01
            delta_transform = trimesh.transformations.translation_matrix(
                [0, 0, -plane_thick / 2]
            )
            tm = trimesh.creation.box(
                extents=[1.0, 1.0, plane_thick], transform=delta_transform
            )
        else:
            raise NotImplementedError("Unsupported object type")

        rotation_matrix = trimesh.transformations.quaternion_matrix(obj["pose"][3:])
        rotation_matrix[:3, 3] = obj["pose"][:3]
        tm.apply_transform(rotation_matrix)
        tm_lst.append(tm)
    scene_mesh = trimesh.util.concatenate(tm_lst)
    return scene_mesh


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
        camera_type="kinect",
    ):
        # tile width and height: the size of each tile
        # n_cols and n_rows: the number of columns and rows
        # screnn_width=tile_width*n_cols, screen_height=tile_height*n_rows
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

    def update_camera_poses(self, view_matrix):
        self.view_matrix = torch.tensor(view_matrix).to(self.device).float()
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

    def render(self, obj_mesh, camera_view_matrix):
        self.renderer.clear()
        self.update_camera_poses(camera_view_matrix)
        time = self.renderer.clock_time
        self.renderer.begin_frame(time)
        self.renderer.render_mesh(
            name="mesh", points=obj_mesh.vertices, indices=obj_mesh.faces
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


def batch_warp_render(configs, scene_cfg_path_lst, gpu_id):
    func_config = configs.func
    device = f"cuda:{gpu_id}"
    with wp.ScopedDevice(device):
        renderer = WarpRender(device)

        output_folder = func_config.save_path.split("/**")[0]
        os.makedirs(output_folder, exist_ok=True)
        np.save(
            os.path.join(output_folder, "cam_in.npy"),
            renderer.projection_matrixs[0],
        )

        for scene_cfg_path in tqdm(scene_cfg_path_lst):
            scene_cfg = np.load(scene_cfg_path, allow_pickle=True).item()

            batch = renderer.num_tiles
            scene_pc_folder = func_config.save_path.replace("**", scene_cfg["scene_id"])

            # check path
            if configs.skip:
                conti_flag = True
                for b in range(batch):
                    pc_path = os.path.join(
                        scene_pc_folder, f"partial_pc_{str(b).zfill(2)}.npy"
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

            obj_name = scene_cfg["task"]["obj_name"]
            obj_mesh = scene_cfg2mesh(scene_cfg, scene_cfg_path)
            scene_cfg["camera"]["sample_num"] = batch
            camera_view_matrix = get_camera_matrix(scene_cfg["camera"])

            view_matrix = renderer.render(obj_mesh, camera_view_matrix)

            if func_config.save_rgb:
                rgb_image = renderer.get_image(mode="rgb")

            if func_config.save_depth or func_config.save_pc:
                depth_image = renderer.get_image(mode="depth")
                if func_config.save_pc:
                    all_pc = renderer.depth_to_point_cloud(depth_image)
                    mask = depth_image.reshape(batch, -1) < 5

            # save informations
            for b in range(batch):
                os.makedirs(scene_pc_folder, exist_ok=True)
                data_id = str(b).zfill(2)
                np.save(
                    os.path.join(scene_pc_folder, f"cam_ex_{data_id}.npy"),
                    view_matrix[b].cpu().numpy(),
                )
                if func_config.save_rgb:
                    cv2.imwrite(
                        os.path.join(scene_pc_folder, f"rgb_{data_id}.png"),
                        rgb_image[b].cpu().numpy() * 255,
                    )
                if func_config.save_depth:
                    cv2.imwrite(
                        os.path.join(scene_pc_folder, f"depth_{data_id}.png"),
                        depth_image[b].cpu().numpy(),
                    )
                if func_config.save_pc:
                    pc = all_pc[b, mask[b]]
                    pc = pc[torch.randperm(pc.shape[0])[: func_config.max_point_num]]
                    np.save(
                        os.path.join(scene_pc_folder, f"partial_pc_{data_id}.npy"),
                        pc.cpu().numpy().astype(np.float16),
                    )
