from typing import Dict, List
import os
import json 
import logging 
from filelock import FileLock

import yaml
from yaml import Loader


class SafeLogger:
    def __init__(self, log_path, level=logging.ERROR):
        logging.basicConfig(filename=log_path, 
                            format='%(asctime)s - %(levelname)s - %(message)s', 
                            level=level,
                            filemode='w'
                        )
        self.lock = FileLock(log_path+'.lock')
        self.logger = logging.getLogger()
        
    def log_error(self, str):
        with self.lock:
            self.logger.error(str)
    
    def log_warn(self, str):
        with self.lock:
            self.logger.warning(str)
            
    def log_info(self, str):
        with self.lock:
            self.logger.info(str)
            
logger = SafeLogger(os.path.join(os.path.dirname(__file__), 'logger.log'), level=logging.ERROR)

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

def get_config(dataset_name):
    config = load_yaml(os.path.join(os.path.dirname(__file__), 'config.yml'))
    config['dataset_root'] = config.pop('root_candidates')[dataset_name]
    config['processed_folder'] = os.path.join(config['dataset_root'], config['processed_folder'])
    return config


def ensure_path(func):
    def wrapper(*args, **kwargs):
        config = args[0]
        if isinstance(config, dict) and 'output_path' in config.keys():
            if not os.path.exists(config['input_path']):
                logger.log_error(f"Stop task {func.__name__}: input path does not exist in {config['input_path']}")
                raise Exception
            if os.path.exists(config['output_path']) and config['skip']:
                logger.log_info(f"Skip task {func.__name__}: output path already exist in {config['output_path']}")
                return 
            os.makedirs(os.path.dirname(config['output_path']), exist_ok=True)
        output = func(*args, **kwargs)
        logger.log_info(f"Finish task {func.__name__}.")
        return output
    return wrapper
