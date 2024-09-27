import argparse
from glob import glob 
import os 
import time 
import sys 

from pytorch3d.io import load_objs_as_meshes
from pytorch3d.ops import sample_points_from_meshes
from pytorch3d.loss import chamfer_distance

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import get_config

if __name__ == '__main__':
    path_cfg = get_config('customized')
    
    simp_lst = glob(os.path.join(path_cfg['processed_folder'], '**', path_cfg['mesh_simplified']))

    device = 'cuda:0'
    # st = time.time()
    # pt_meshes = load_objs_as_meshes(simp_lst[:200], device=device)
    # print('read', time.time()-st)
    
    # st = time.time()
    # samples = sample_points_from_meshes(pt_meshes, num_samples=1024)
    # print('sample', time.time()-st)

    # pt_meshes2 = load_objs_as_meshes(simp_lst[200:400], device=device)
    # samples2 = sample_points_from_meshes(pt_meshes2, num_samples=1024)
    
    st = time.time()
    all_chamfers, _ = chamfer_distance(samples, samples2, batch_reduction=None)
    print(all_chamfers.mean())
    print(time.time()-st)
    import pdb;pdb.set_trace()
    