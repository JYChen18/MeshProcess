import sys 
import os 
import argparse

from tqdm.contrib.concurrent import process_map 
import trimesh

SRC_FOLDER = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(SRC_FOLDER)
from util_file import load_yaml, load_json

data_cfg = load_yaml(os.path.join(SRC_FOLDER, 'config/data/objaverse.yaml'))
data_cfg['processed_folder'] = data_cfg['processed_folder'].replace("${data.root}", data_cfg['root'])
task_cfg = load_yaml(os.path.join(SRC_FOLDER, 'config/task/main.yaml'))

def glb2obj(glb_path, skip):
    obj_name = glb_path.split('/')[-1].replace('.glb', '')
    out_path = os.path.join(data_cfg['processed_folder'], obj_name, task_cfg['1-mesh_normalize']['input_path'])
    if os.path.exists(glb_path) and (not os.path.exists(out_path) or not skip):
        obj = trimesh.load(glb_path, force='mesh')
        obj.visual = trimesh.visual.ColorVisuals()  # remove material
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        try:
            obj.export(out_path)
        except:
            print(f'Fail {glb_path}')
    return 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--skip', action='store_false')
    args = parser.parse_args()
    
    raw_folder = os.path.join(data_cfg['root'], 'hf-objaverse-v1')
    json_path = os.path.join(raw_folder, 'object-paths.json')

    # unzip object-paths.json.gz
    if not os.path.exists(json_path):
        json_zip_path = json_path + '.gz'
        assert os.path.exists(json_zip_path)
        os.system(f'gzip -d {json_zip_path}')
        
    path_dict = load_json(json_path)

    glb_path_lst = [os.path.join(raw_folder, value) for value in path_dict.values()]
    skip_lst = [args.skip] * len(glb_path_lst)
    process_map(glb2obj, glb_path_lst, skip_lst, max_workers=32, chunksize=1)
    