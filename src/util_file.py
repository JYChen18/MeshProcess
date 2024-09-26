from typing import Dict, List
import os
import json 
import yaml
from yaml import Loader
import multiprocessing
from tqdm import tqdm

def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def write_json(data: Dict, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=1)
    return 

def load_yaml(file_path) -> Dict:
    with open(file_path) as file_p:
        data = yaml.load(file_p, Loader=Loader)
    return data

def get_path_cfg(dataset_name):
    path_cfg = load_yaml(os.path.join(os.path.dirname(__file__), 'path_cfg.yml'))
    path_cfg['dataset_root'] = path_cfg.pop('root_candidates')[dataset_name]
    path_cfg['processed_folder'] = os.path.join(path_cfg['dataset_root'], path_cfg['processed_folder'])
    return path_cfg

def run_multiprocess(worker, params_lst, n_process=10):
    def handle_error(e):
        print(f'Error occurred: {e}')  # Print the error message

    with multiprocessing.Pool(processes=n_process) as pool:
        for params in tqdm(params_lst):
            input_params = (params, ) if not isinstance(params, tuple) else params
            pool.apply_async(worker, input_params, error_callback=handle_error)
        pool.close()  # Prevent any more tasks from being submitted
        pool.join()   # Wait for the worker processes to exit
    return 