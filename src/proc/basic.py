import sys
import os 
import trimesh 
import numpy as np
import lxml.etree as et
import glob 

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import write_json, ensure_path

# save basic info
@ensure_path
def _get_basic_info(config):
    input_path, output_path = config['input_path'], config['output_path']
    tm_mesh = trimesh.load(input_path, force='mesh')
    obb_length = tm_mesh.bounding_box_oriented.primitive.extents
    gravity_center = tm_mesh.center_mass
    write_json({'gravity_center': gravity_center.tolist(),
                'obb': obb_length.tolist()
                },
               output_path)
    return 

# save complete point cloud
@ensure_path
def _get_complete_pc(config):
    input_path, output_path, point_num = config['input_path'], config['output_path'], config['point_num']
    tm_mesh = trimesh.load(input_path, force='mesh')
    complete_pc, _ = trimesh.sample.sample_surface(tm_mesh, point_num)
    np.save(output_path, complete_pc.astype(np.float16))
    return 

@ensure_path
def _export_urdf(config):
    input_path, output_path = config['input_path'], config['output_path']
    
    parts = trimesh.load(input_path, force='mesh').split()
    # open an XML tree
    root = et.Element('robot', name='root')
    
    # Loop through all pieces, adding each as a link
    prev_link_name = None
    for i, piece in enumerate(parts):
        # Save each nearly convex mesh out to a file
        piece_name = f'convex_piece_{i}'
        piece_filename = f'convex_piece_{i}.obj'
        piece_filepath = os.path.join(os.path.dirname(output_path), 'meshes', piece_filename)
        os.makedirs(os.path.dirname(piece_filepath), exist_ok=True)
        piece.export(piece_filepath)
        
        link_name = 'link_{}'.format(piece_name)
        I = [['{:.2E}'.format(y) for y in x]  # NOQA
            for x in piece.moment_inertia]

        # Write the link out to the XML Tree
        link = et.SubElement(root, 'link', name=link_name)

        # Inertial information
        inertial = et.SubElement(link, 'inertial')
        et.SubElement(inertial, 'origin', xyz="0 0 0", rpy="0 0 0")
        # et.SubElement(inertial, 'mass', value='{:.2E}'.format(piece.mass))
        et.SubElement(
            inertial,
            'inertia',
            ixx=I[0][0],
            ixy=I[0][1],
            ixz=I[0][2],
            iyy=I[1][1],
            iyz=I[1][2],
            izz=I[2][2])
        
        # Visual Information
        visual = et.SubElement(link, 'visual')
        et.SubElement(visual, 'origin', xyz="0 0 0", rpy="0 0 0")
        geometry = et.SubElement(visual, 'geometry')
        et.SubElement(geometry, 'mesh', filename=piece_filename, scale="1.0 1.0 1.0")
        
        # Collision Information
        collision = et.SubElement(link, 'collision')
        et.SubElement(collision, 'origin', xyz="0 0 0", rpy="0 0 0")
        geometry = et.SubElement(collision, 'geometry')
        et.SubElement(geometry, 'mesh', filename=piece_filename, scale="1.0 1.0 1.0")

        # Create rigid joint to previous link
        if prev_link_name is not None:
            joint_name = '{}_joint'.format(link_name)
            joint = et.SubElement(root,
                                'joint',
                                name=joint_name,
                                type='fixed')
            et.SubElement(joint, 'origin', xyz="0 0 0", rpy="0 0 0")
            et.SubElement(joint, 'parent', link=prev_link_name)
            et.SubElement(joint, 'child', link=link_name)

        prev_link_name = link_name

    # Write URDF file
    tree = et.ElementTree(root)
    tree.write(output_path, pretty_print=True)
    return 

@ensure_path
def _remove_useless(config):
    pass

@ensure_path
def _clean_all(config):
    input_path, clean_path = config['input_path'], config['clean_path']
    all_lst = glob.glob(os.path.join(os.path.abspath(clean_path), '**'), recursive=True)
    for p in all_lst:
        if os.path.isdir(p):
            if not os.path.commonprefix([p, input_path]) == p:
                os.system(f'rm -r {p}') 
        else:
            if not os.path.samefile(p, input_path):
                os.system(f'rm {p}') 
    return 

# def export_xml(config):
#     raise NotImplementedError

