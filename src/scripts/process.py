import os 
import sys 
import logging 
import traceback

from tqdm.contrib.concurrent import process_map 

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import get_config
from proc.mesh import _manifold, _coacd, _simplify
from proc.basic import _get_basic_info, _get_complete_pc

def process_all(obj_code):
    # read config
    all_config = get_config('customized')
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
    config = get_config('customized')
    obj_lst = os.listdir(config['processed_folder'])
        
    process_map(process_all, obj_lst, max_workers=config['n_process'], chunksize=1)
    
    