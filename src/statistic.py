import os 
import argparse
from glob import glob

from preprocess import MeshProcess

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type=str, required=True)
    args = parser.parse_args()
    
    raw_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['raw']))
    coacd_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['coacd']))
    mani_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['manifold']))
    simp_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['simplified']))
    info_lst = glob(os.path.join(args.folder, '**', MeshProcess.relative_path['info']))
    
    print('Raw object number: ', len(raw_lst))
    print('CoACD success rates: ', len(coacd_lst) / len(raw_lst))
    print('Manifold success rates: ', len(mani_lst) / len(coacd_lst))
    print('Simplify success rates: ', len(simp_lst) / len(mani_lst))
    print('Total success rates: ', len(info_lst) / len(raw_lst))
    