import argparse
from glob import glob 
import os 
import time 

from pytorch3d.io import load_objs_as_meshes
from pytorch3d.ops import sample_points_from_meshes
from pytorch3d.loss import chamfer_distance

from preprocess import MeshProcess

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type=str, default='/mnt/disk0/objaverse/mesh_v1', help='the path to the data directory')
    args = parser.parse_args()
    
    simp_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['mesh_simplified']))

    device = 'cuda:0'
    st = time.time()
    pt_meshes = load_objs_as_meshes(simp_lst[:200], device=device)
    print('read', time.time()-st)
    
    st = time.time()
    samples = sample_points_from_meshes(pt_meshes, num_samples=1024)
    print('sample', time.time()-st)

    pt_meshes2 = load_objs_as_meshes(simp_lst[200:400], device=device)
    samples2 = sample_points_from_meshes(pt_meshes2, num_samples=1024)
    
    st = time.time()
    all_chamfers, _ = chamfer_distance(samples, samples2, batch_reduction=None)
    print(all_chamfers.mean())
    print(time.time()-st)
    import pdb;pdb.set_trace()
    