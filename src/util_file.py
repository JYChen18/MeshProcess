import json 
from typing import Dict, List

OBJAVERSE_ROOT = '/mnt/disk0/objaverse'

def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def write_json(data: Dict, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=1)
    return 