import os
import sys
import numpy as np
import trimesh 
import coacd 
coacd.set_log_level("error")

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import ensure_path

@ensure_path
def _simplify(config):
    input_path, output_path, vert_num, gradation = config['input_path'], config['output_path'], config['vert_num'], config['gradation']
    os.system(f'third_party/ACVD/bin/ACVD {input_path} {vert_num} {gradation} -o {os.path.dirname(output_path)+os.sep} -of {os.path.basename(output_path)} -m 1 > /dev/null 2>&1')
    return

@ensure_path
def _normalize(config):
    input_path, output_path = config['input_path'], config['output_path']
    tm_mesh = trimesh.load(input_path, force='mesh')
    verts = np.array(tm_mesh.vertices)
    center = (np.max(verts, axis=0) + np.min(verts, axis=0)) / 2
    length = np.linalg.norm(np.max(verts, axis=0) - np.min(verts, axis=0)) / 2
    tm_mesh.vertices = (verts - center) / length
    tm_mesh.export(output_path)
    return 

@ensure_path
def _coacd(config):
    input_path, output_path = config['input_path'], config['output_path']
    os.system(f'third_party/CoACD/build/main -i {input_path} -o {output_path} > /dev/null 2>&1')
    return 

@ensure_path
def _manifold(config):
    input_path, output_path = config['input_path'], config['output_path']
    os.system(f'third_party/CoACD/build/main -i {input_path} -ro {output_path} -pm on > /dev/null 2>&1')
    return 

@ensure_path
def _change_mesh_format(config):
    input_path, output_path = config['input_path'], config['output_path']
    tm_mesh = trimesh.load(input_path, force='mesh')
    tm_mesh.export(output_path)
    return 
