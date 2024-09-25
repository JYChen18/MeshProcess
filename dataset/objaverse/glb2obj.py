import trimesh
from util_file import OBJAVERSE_ROOT, load_json
import os 

raw_folder = os.path.join(OBJAVERSE_ROOT, 'hf-objaverse-v1')
json_path = os.path.join(raw_folder, 'object-paths.json')
output_folder = os.path.join(OBJAVERSE_ROOT, 'obj_v1')

if not os.path.exists(json_path):
    json_zip_path = json_path + '.gz'
    assert os.path.exists(json_zip_path)
    os.system(f'gzip -d {json_zip_path}')
    
path_dict = load_json(json_path)

for k, v in path_dict.items():
    path = os.path.join(raw_folder, v)
    if os.path.exists(path):
        obj = trimesh.load(path, force='mesh')
        obj_name = path.split('/')[-1].replace('.glb', '.obj')
        out_path = os.path.join(output_folder, obj_name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        obj.export(out_path)
        