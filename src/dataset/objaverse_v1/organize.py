import sys 
import os 
import argparse

from tqdm.contrib.concurrent import process_map 
import trimesh

SRC_FOLDER = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(SRC_FOLDER)
from util_file import load_json

def create_softlink(input_path, output_path):
    if os.path.exists(input_path) and not os.path.exists(output_path):
        os.system(f'ln -s {input_path} {output_path}')
    return 

if __name__ == '__main__':
    raw_folder = os.path.join(os.path.expanduser('~'), '.objaverse/hf-objaverse-v1')
    output_folder = os.path.join(raw_folder, 'organized_glbs')
    os.makedirs(output_folder, exist_ok=True)
    
    json_path = os.path.join(raw_folder, 'object-paths.json')

    # unzip object-paths.json.gz
    if not os.path.exists(json_path):
        json_zip_path = json_path + '.gz'
        assert os.path.exists(json_zip_path)
        os.system(f'gzip -d {json_zip_path}')
        
    path_dict = load_json(json_path)

    input_path_lst = [os.path.join(raw_folder, value) for value in path_dict.values()]
    output_path_lst = [os.path.join(output_folder, key+'.glb') for key in path_dict.keys()]
    process_map(create_softlink, input_path_lst, output_path_lst, max_workers=32, chunksize=1)
    