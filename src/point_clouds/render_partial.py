import os
import argparse

import pyglet
pyglet.options['headless'] = True
import numpy as np
import warp as wp
import warp.render
import torch 
import trimesh
os.environ["DISPLAY"] = ":98"# useless?
import cv2
from tqdm import tqdm

from util_file import load_json

def create_view_matrix(position, target):
    # position: the position of the camera
    # target: the position of the object
    # return: the view matrix in opengl format
    front=np.array(target)-np.array(position)
    front=front/np.linalg.norm(front)
    while(1):
        up=np.random.rand(3)
        up/=np.linalg.norm(up)
        if(np.linalg.norm(np.cross(front,up))>0.1):
            break
    up=up-np.dot(up,front)*front
    up=up/np.linalg.norm(up)
    side=np.cross(front,up)
    view_matrix=np.eye(4)
    view_matrix[3,:3]=np.array(position)
    view_matrix[2,:3]=-front
    view_matrix[1,:3]=up
    view_matrix[0,:3]=side
    return torch.tensor(view_matrix)

def fibonacci_sphere(samples=1, radius=1.0,offset=np.array([0, 0, 0])):
    #return: a list of points on the sphere with the center at offset and the radius of radius
    points = []
    phi = np.pi * (3.0 - np.sqrt(5.0))  # golden angle in radians
    for i in range(samples):
        theta = phi * i  # golden angle increment
        x = np.cos(theta)
        y = np.sin(theta)
        z=0.1*np.random.random()/radius
        points.append(np.array([x, y, z]) * (radius+0.1*np.random.random()-0.05) + offset)
    return points
    
    

class WarpRender:
    def __init__(self, device, tile_width=1280, tile_height=720, z_near=0.1, z_far=10.0, n_cols=2, n_rows=2, radius=0.8, camera_type='kinect'):
        # tile width and height: the size of each tile
        # n_cols and n_rows: the number of columns and rows
        # screnn_width=tile_width*n_cols, screen_height=tile_height*n_rows
        self.radius = radius
        self.device = device
        
        self.ncols = n_cols
        self.nrows = n_rows
        self.num_tiles = n_cols*n_rows
        self.tile_width = tile_width
        self.tile_height = tile_height
        
        self.renderer =wp.render.OpenGLRenderer(
            draw_axis=False, draw_grid=False, show_info=False, draw_sky=False,
            screen_width=tile_width*n_cols, screen_height=tile_height*n_rows,
            near_plane=z_near, far_plane=z_far, vsync=False,headless=True)

        # setup intrinsics
        self.cx = tile_width // 2
        self.cy = tile_height // 2
        
        if camera_type == 'kinect':
            self.fx = 608.6939697265625
            self.fy = 608.6422119140625
        else:
            raise NotImplementedError
        
        self.projection_matrixs = [np.array([
                    [2 * self.fx / tile_width,        0,     0,   0],
                    [       0,2 * self.fy / tile_height,     0,   0],
                    [0, 0,  -(z_far + z_near) / (z_far - z_near),  -1],
                    [0, 0,  -2 * z_far * z_near / (z_far - z_near), 0]
                ])] * self.num_tiles

        self.setup_tile_flag = False
        self.help_yy, self.help_xx = torch.meshgrid(torch.arange(self.tile_height).to(self.device), torch.arange(self.tile_width).to(self.device))
        self.help_xx = self.help_xx[None, :, :, None]
        self.help_yy = self.help_yy[None, :, :, None]
        return 
    
    def update_tile_poses(self, obj_trans):
        camera_positions = fibonacci_sphere(self.num_tiles,radius = self.radius,offset=np.array([0, 0, self.radius]))
        view_matrix = [create_view_matrix(camera_positions[i], obj_trans) for i in range(self.num_tiles)]
        self.view_matrix = torch.stack(view_matrix).to(self.device).float()
        inv_view_matrix =  torch.inverse(self.view_matrix).tolist()
        
        if not self.setup_tile_flag:
            self.renderer.setup_tiled_rendering(instances=[[0]]*self.num_tiles,
                                            tile_sizes=[(self.tile_width, self.tile_height)]*self.num_tiles,
                                            projection_matrices=self.projection_matrixs,
                                            view_matrices=inv_view_matrix,
                                            tile_ncols=self.ncols,
                                            tile_nrows=self.nrows
                                        )
            self.setup_tile_flag = True
        else:    
            for id in range(self.num_tiles):
                self.renderer.update_tile(tile_id=id,
                                    instances=[0],
                                    tile_size=(self.tile_width, self.tile_height),
                                    projection_matrix=self.projection_matrixs[id],
                                    view_matrix=inv_view_matrix[id]
                                )
        return
        
    def get_image(self, mode='depth', save_path=None):
        if mode == 'depth' and save_path is None:
            image = wp.zeros((self.num_tiles,self.tile_height,self.tile_width,1),dtype=wp.float32)
        elif mode == 'rgb' or save_path is not None:
            image = wp.zeros((self.num_tiles,self.tile_height,self.tile_width,3),dtype=wp.float32)
        else:
            raise NotImplementedError
        
        self.renderer.get_pixels(image, split_up_tiles=True, mode=mode)
        
        if save_path is not None:
            os.makedirs(save_path, exist_ok=True)
            for i in range(self.num_tiles):
                cv2.imwrite(os.path.join(save_path, f'rgb{i}.png'),np.squeeze(image.numpy()[i])*255)
        return wp.to_torch(image)    
    
    def render(self, obj_mesh, obj_scale, obj_trans, obj_rot):
        self.renderer.clear()
        self.update_tile_poses(obj_trans)
        time=self.renderer.clock_time
        self.renderer.begin_frame(time) 
        self.renderer.render_mesh(name='mesh', points=obj_mesh.vertices, indices=obj_mesh.faces, pos=obj_trans, scale=obj_scale, rot=obj_rot)
        self.renderer.end_frame()
        return self.view_matrix
    
    def depth_to_point_cloud(self, depth_image):
        x = (self.help_xx - self.cx) * depth_image / self.fx
        y = - (self.help_yy - self.cy) * depth_image / self.fy
        camera_coords = torch.cat([x, y, -depth_image, torch.ones_like(x, device=x.device)], axis=-1)
        world_coords = camera_coords.view(depth_image.shape[0], -1, 4) @ self.view_matrix
        return world_coords[...,:3]
        

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type=str, default='/mnt/disk1/jiayichen/data/dex_obj/meshdata', help='the path to the data directory')
    parser.add_argument('-o', '--output_folder', type=str, default='kinect_table_pc', help='saved path relative to the args.folder')
    parser.add_argument('-l', '--scale_lst', type=float, nargs='+', default=[0.06, 0.08, 0.10, 0.12], help='object scales')
    parser.add_argument('-debug', '--debug_dir', type=str, default=None, help='the path to save the images')
    parser.add_argument('-k', '--skip', action='store_false', help='whether to skip exist files (default: True)')
    parser.add_argument('-g', '--gpu', type=int, default=0, help='gpu id')
    parser.add_argument('-s', '--start', type=int, default=0, help='start obj id')
    parser.add_argument('-e', '--end', type=int, default=100, help='end obj id')
    args = parser.parse_args()
    
    device = f'cuda:{args.gpu}'
    
    with wp.ScopedDevice(device):
        renderer = WarpRender(device)
        
        obj_lst = sorted(os.listdir(args.folder))[args.start:args.end]
        
        for obj_code in tqdm(obj_lst):
            
            obj_path = os.path.join(args.folder, obj_code, 'mesh/simplified.obj')
            obj_mesh = trimesh.load(obj_path)
            complete_pc, _ = trimesh.sample.sample_surface(obj_mesh, 8192)
            
            table_pose_path = os.path.join(args.folder, obj_code, 'tabletop_pose.json')
            if not os.path.exists(table_pose_path):
                continue
            table_pose_anno = load_json(table_pose_path)
            
            obj_newf_path = os.path.join(args.folder, obj_code, args.output_folder)
            os.makedirs(obj_newf_path, exist_ok=True)
            np.save(os.path.join(obj_newf_path, 'cam_in.npy'), renderer.projection_matrixs[0])
            
            for scale in args.scale_lst:
                pose_lst = table_pose_anno[str(scale)]
                obj_scale_path = os.path.join(obj_newf_path, f'scale{str(int(scale*100)).zfill(3)}')
            
                for pose_num, pose in enumerate(pose_lst):
                    batch = renderer.num_tiles
                    obj_pose_path = os.path.join(obj_scale_path, f'pose{str(pose_num).zfill(3)}')
                    
                    # check path
                    if args.skip:
                        conti_flag = True
                        for b in range(batch):
                            pc_path = os.path.join(obj_pose_path, f'partial_pc_{str(b).zfill(2)}.npy')
                            if not os.path.exists(pc_path):
                                conti_flag = False
                                break
                            else:
                                check_pc = np.load(pc_path, allow_pickle=True)
                                if len(check_pc) == 0:
                                    print(f'Point number is 0 ! {pc_path}')
                                    conti_flag = False
                        if conti_flag:
                            print(f'Skip {pc_path}')
                            continue
                    
                    obj_scale = np.array([scale, scale, scale])
                    obj_trans = pose[:3]
                    obj_rot = np.array(pose)[[4,5,6,3]]
                    
                    view_matrix = renderer.render(obj_mesh, obj_scale, obj_trans, obj_rot)
                    
                    depth_image = renderer.get_image(mode='depth', save_path=args.debug_dir)
                    
                    all_pc = renderer.depth_to_point_cloud(depth_image)
                    mask = depth_image.reshape(batch, -1) < 5
                    
                    # save informations
                    for b in range(batch):
                        pc = all_pc[b, mask[b]]
                        os.makedirs(obj_pose_path, exist_ok=True)
                        np.save(os.path.join(obj_pose_path, f'cam_ex_{str(b).zfill(2)}.npy'), view_matrix[b].cpu().numpy())
                        np.save(os.path.join(obj_pose_path, f'partial_pc_{str(b).zfill(2)}.npy'), pc.cpu().numpy().astype(np.float16))
                        
                    
                    
            
        
        
        
        
