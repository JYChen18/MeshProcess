import os 
import argparse
from glob import glob
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mesh.preprocess import MeshProcess

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type=str, default='/mnt/disk0/objaverse/mesh_v1', help='the path to the data directory')
    args = parser.parse_args()
    
    raw_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['mesh_raw']))
    coacd_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['mesh_coacd']))
    mani_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['mesh_manifold']))
    simp_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['mesh_simplified']))
    info_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['info_simplified']))
    
    print('Raw object number: ', len(raw_lst))
    print('CoACD success rates: ', len(coacd_lst) / len(raw_lst))
    print('Manifold success rates: ', len(mani_lst) / len(coacd_lst))
    print('Simplify success rates: ', len(simp_lst) / len(mani_lst))
    print('Total success rates: ', len(info_lst) / len(raw_lst))
    