import os 
import sys 
import argparse

from tqdm.contrib.concurrent import process_map 

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import get_config
from proc.mesh import _manifold, _normalize, _coacd, _simplify, _change_mesh_format
from proc.basic import _get_basic_info, _get_complete_pc, _export_urdf, _remove_useless, _clean_all

def process_all(obj_code, config_name):
    # read config
    all_config = get_config(config_name, 'customized')
    for task_name, task_cfg in all_config['tasks'].items():
        task_cfg['skip'] = all_config['skip']
        for k, v in task_cfg.items():
            if k.endswith('_path'):
                task_cfg[k] = os.path.join(all_config['processed_folder'], obj_code, v)
        try:
            eval(task_name)(task_cfg)
        except:
            break
    return 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_name', type=str, default='main')
    args = parser.parse_args()
    
    config = get_config(args.config_name, 'customized')
    obj_lst = os.listdir(config['processed_folder'])
    config_name_lst = [args.config_name] * len(obj_lst)
    
    process_map(process_all, obj_lst, config_name_lst, max_workers=config['n_process'], chunksize=1)
    
    