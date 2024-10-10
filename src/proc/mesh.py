import os
import sys
import numpy as np
import trimesh 

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import task_wrapper


@task_wrapper
def mesh_normalize(config):
    input_path, output_path = config['input_path'], config['output_path']
    tm_mesh = trimesh.load(input_path, force='mesh')
    verts = np.array(tm_mesh.vertices)
    center = (np.max(verts, axis=0) + np.min(verts, axis=0)) / 2
    length = np.linalg.norm(np.max(verts, axis=0) - np.min(verts, axis=0)) / 2
    tm_mesh.vertices = (verts - center[None]) / length
    tm_mesh.export(output_path)
    return 


@task_wrapper
def mesh_convex_decomp(config):
    input_path, output_path, quiet = config['input_path'], config['output_path'], config['quiet']
    command = f'third_party/CoACD/build/main -i {input_path} -o {output_path}'
    if quiet:
        command += ' > /dev/null 2>&1'
    os.system(command)
    return 


@task_wrapper
def mesh_manifold(config):
    input_path, output_path, quiet = config['input_path'], config['output_path'], config['quiet']
    command = f'third_party/CoACD/build/main -i {input_path} -ro {output_path} -pm on'
    if quiet:
        command += ' > /dev/null 2>&1'
    os.system(command)
    return 


@task_wrapper
def mesh_simplify(config):
    input_path, output_path, vert_num, gradation, quiet = config['input_path'], config['output_path'], config['vert_num'], config['gradation'], config['quiet']
    command = f'third_party/ACVD/bin/ACVD {input_path} {vert_num} {gradation} -o {os.path.dirname(output_path)+os.sep} -of {os.path.basename(output_path)} -m 1'
    if quiet:
        command += ' > /dev/null 2>&1'
    os.system(command)
    os.system(f"rm {os.path.join(os.path.dirname(output_path), 'smooth_'+os.path.basename(output_path))}")
    return


@task_wrapper
def mesh_change_format(config):
    input_path, output_path, keep_material = config['input_path'], config['output_path'], config['keep_material']
    tm_mesh = trimesh.load(input_path, force='mesh')
    if not keep_material:
        tm_mesh.visual = trimesh.visual.ColorVisuals()  
    tm_mesh.export(output_path)
    return 
