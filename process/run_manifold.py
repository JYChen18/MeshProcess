import os
import sys
import argparse
import multiprocessing
from rich.progress import track

def manifold(input_path):
    output_path = input_path[:-4] + '_manifold' + input_path[-4:]
    command = f'{args.manifoldplus_path} {input_path} {output_path} {args.resolution}'
    command += '> /dev/null 2>&1'
    os.system(command)
    return 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifoldplus_path', type=str, 
        default='../third_party/Manifold/build/manifold')
    parser.add_argument('--obj_list_file', type=str, 
        default='all_obj_path.txt')
    parser.add_argument('--n_cpu', type=int, default=10)
    parser.add_argument('--resolution', type=int, default=10000)
    args = parser.parse_args()
    with open(args.obj_list_file, 'r') as f:
        obj_lst = f.readlines()
    obj_lst = [f.split('\n')[0] for f in obj_lst]
    
    # manifold with process pool
    with multiprocessing.Pool(processes=args.n_cpu) as pool:
        it = track(
            pool.imap_unordered(manifold, obj_lst), 
            total=len(obj_lst), 
            description='manifolding', 
        )
        list(it)