import os
import argparse

import numpy as np
import trimesh
from tqdm import tqdm
    
    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type=str, default='/mnt/disk0/objaverse/mesh_v1', help='the path to the data directory')
    parser.add_argument('-k', '--skip', action='store_false', help='whether to skip exist files (default: True)')
    args = parser.parse_args()
    
    obj_lst = os.listdir(args.folder)
    for obj_code in tqdm(obj_lst):  
        mesh_path = os.path.join(args.folder, obj_code, 'mesh/simplified.obj')
        save_path = os.path.join(args.folder, obj_code, 'point_clouds/complete.npy')
        
        if os.path.exists(mesh_path) and (not os.path.exists(save_path) or not args.skip):
            obj_mesh = trimesh.load(mesh_path, force='mesh')
            complete_pc, _ = trimesh.sample.sample_surface(obj_mesh, 4096)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            np.save(save_path, complete_pc.astype(np.float16))
                