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
    cfg, obj_id = params
    # read config
    new_task_cfg = deepcopy(cfg['task'])
    for task_name, task_cfg in new_task_cfg.items():
        func_name = task_name.split('-')[-1]
        for k, v in task_cfg.items():
            if k.endswith('_path'):
                task_cfg[k] = os.path.abspath(v.replace('**', obj_id))
        try:
            eval(func_name)(task_cfg, logger=logger, skip=cfg['skip'], debug=cfg['debug_id'] is not None)
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.info(f'Failure! Task: {task_name}, obj: {obj_id} \n {error_traceback}')
            return
    logger.info(f'Success! obj: {obj_id}')
    return 

@hydra.main(config_path="../config", config_name="base", version_base=None)
def main(cfg: DictConfig) -> None:
    assert '**' in cfg['data']['input_template'] and len(cfg['data']['input_template'].split('**')) == 2
    full_path_lst = glob.glob(cfg['data']['input_template'], recursive=True)
    prefix = cfg['data']['input_template'].split('**')[0]
    suffix = cfg['data']['input_template'].split('**')[1] 
    obj_lst = [p.replace(prefix, '').replace(suffix, '') for p in full_path_lst]

    logger.info("#"*30)
    logger.info(f"Input template: {cfg['data']['input_template']}")
    logger.info(f"Output template: {cfg['data']['output_template']}")
    logger.info(f"Object Number: {len(obj_lst)}")
    logger.info(f"Tasks: {list(cfg['task'].keys())}")
    logger.info("#"*30)
    
    if cfg['debug_id'] is not None:
        process_all((cfg, cfg['debug_id']))
    else:
        iterable_params = [(cfg, obj_id) for obj_id in obj_lst]
        with multiprocessing.Pool(processes=cfg['n_worker']) as pool:
            result_iter = pool.imap_unordered(process_all, iterable_params)
            results = list(result_iter)
    return 

if __name__ == '__main__':
   main()