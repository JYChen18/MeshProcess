import os 
import sys 
from copy import deepcopy
import logging 
import traceback
import multiprocessing

import hydra
from omegaconf import DictConfig

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from proc.mesh import *
from proc.basic import *

logger = logging.getLogger('Process')

def process_all(params):
    cfg, obj_code = params
    # read config
    new_task_cfg = deepcopy(cfg['task'])
    for task_name, task_cfg in new_task_cfg.items():
        func_name = task_name.split('-')[-1]
        for k, v in task_cfg.items():
            if k.endswith('_path'):
                task_cfg[k] = os.path.abspath(os.path.join(cfg['data']['processed_folder'], obj_code, v))
        try:
            eval(func_name)(task_cfg, logger=logger, skip=cfg['skip'], debug=cfg['debug_id'] is not None)
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.info(f'Failure! Task: {task_name}, obj: {obj_code} \n {error_traceback}')
            return
    logger.info(f'Success! obj: {obj_code}')
    return 

@hydra.main(config_path="../config", config_name="base", version_base=None)
def main(cfg: DictConfig) -> None:
    obj_lst = os.listdir(cfg['data']['processed_folder'])
    logger.info(f"Processing folder: {cfg['data']['processed_folder']}")
    logger.info(f"Object Number: {len(obj_lst)}")
    logger.info(f"Tasks: {list(cfg['task'].keys())}")
    
    if cfg['debug_id'] is not None:
        process_all((cfg, cfg['debug_id']))
    else:
        iterable_params = [(cfg, obj) for obj in obj_lst]
        with multiprocessing.Pool(processes=cfg['n_worker']) as pool:
            result_iter = pool.imap_unordered(process_all, iterable_params)
            results = list(result_iter)
    return 

if __name__ == '__main__':
   main()