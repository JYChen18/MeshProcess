import os
import sys
import numpy as np
import trimesh 
import coacd 
coacd.set_log_level("error")

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import ensure_path
from proc.basic import export_urdf


@ensure_path
def _manifold(config):
    input_path, output_path, depth = config['input_path'], config['output_path'], config['depth']
    os.system(f'third_party/ManifoldPlus/build/manifold --input {input_path} --output {output_path} --depth {depth} > /dev/null 2>&1')
    return

@ensure_path
def _simplify(config):
    input_path, output_path, face_num = config['input_path'], config['output_path'], config['face_num']
    os.system(f'third_party/Manifold/build/simplify -i {input_path} -o {output_path} -f {face_num} -m > /dev/null 2>&1')
    return

def _normalize(tm_mesh):
    verts = np.array(tm_mesh.vertices)
    center = (np.max(verts, axis=0) + np.min(verts, axis=0)) / 2
    length = np.linalg.norm(np.max(verts, axis=0) - np.min(verts, axis=0)) / 2
    tm_mesh.vertices = (verts - center) / length
    return tm_mesh

@ensure_path
def _coacd(config):
    input_path, output_path, normalize_flag, export_urdf_path = config['input_path'], config['output_path'], config['normalize'], config['export_urdf_path']
    tm_mesh = trimesh.load(input_path, force='mesh')
    if normalize_flag:
        tm_mesh = _normalize(tm_mesh)
    mesh = coacd.Mesh(tm_mesh.vertices, tm_mesh.faces)
    parts = coacd.run_coacd(mesh) # a list of convex hulls.
    mesh_parts = []
    for p in parts:
        mesh_parts.append(trimesh.Trimesh(vertices=p[0], faces=p[1]))
    combined = trimesh.util.concatenate(mesh_parts)
    if export_urdf_path is not None:
        export_urdf(export_urdf_path, mesh_parts)
    combined.export(output_path)
    return 


    
