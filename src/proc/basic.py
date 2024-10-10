import sys
import os 
import trimesh 
import numpy as np
import lxml.etree as et
import glob 

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import write_json, task_wrapper

# save basic info
@task_wrapper
def get_basic_info(config):
    input_path, output_path = config['input_path'], config['output_path']
    tm_mesh = trimesh.load(input_path, force='mesh')
    obb_length = tm_mesh.bounding_box_oriented.primitive.extents
    gravity_center = tm_mesh.center_mass
    write_json({'gravity_center': gravity_center.tolist(),
                'obb': obb_length.tolist(),
                'density': tm_mesh.density * 1000,
                'mass': tm_mesh.mass,
                },
               output_path)
    return 

# save complete point cloud
@task_wrapper
def get_complete_pc(config):
    input_path, output_path, point_num = config['input_path'], config['output_path'], config['point_num']
    tm_mesh = trimesh.load(input_path, force='mesh')
    complete_pc, _ = trimesh.sample.sample_surface(tm_mesh, point_num)
    np.save(output_path, complete_pc.astype(np.float16))
    return 

@task_wrapper
def export_urdf(config):
    input_path, export_mesh, output_path = config['input_path'], config['export_mesh'], config['output_path']
    
    parts = trimesh.load(input_path, force='mesh').split()
    root = et.Element('robot', name='root')
    
    prev_link_name = None
    for i, piece in enumerate(parts):
        piece_name = f'convex_piece_{i}'
        piece_filename = f'meshes/convex_piece_{i}.obj'
        piece_filepath = os.path.join(os.path.dirname(output_path), piece_filename)
        if export_mesh:
            os.makedirs(os.path.dirname(piece_filepath), exist_ok=True)
            piece.export(piece_filepath)

        link_name = 'link_{}'.format(piece_name)
        I = [['{:.2E}'.format(y) for y in x]  # NOQA
            for x in piece.moment_inertia]
        link = et.SubElement(root, 'link', name=link_name)
        inertial = et.SubElement(link, 'inertial')
        et.SubElement(inertial, 'origin', xyz="0 0 0", rpy="0 0 0")
        # et.SubElement(inertial, 'mass', value='{:.2E}'.format(piece.mass))
        et.SubElement(inertial, 'inertia', ixx=I[0][0], ixy=I[0][1], ixz=I[0][2],
            iyy=I[1][1], iyz=I[1][2], izz=I[2][2])
        
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


@task_wrapper
def export_mjcf(config):
    input_path, export_mesh, output_path = config['input_path'], config['export_mesh'], config['output_path']
    
    parts = trimesh.load(input_path, force='mesh').split()
    
    asset_mesh_xml = ""
    body_mesh_xml = ""
        
    for i, piece in enumerate(parts):
        piece_name = f'convex_piece_{i}'
        piece_filename = f'meshes/convex_piece_{i}.obj'
        piece_filepath = os.path.join(os.path.dirname(output_path), piece_filename)
        if export_mesh:
            os.makedirs(os.path.dirname(piece_filepath), exist_ok=True)
            piece.export(piece_filepath)

        asset_mesh_xml += f'<mesh name="{piece_name}" file="{piece_filepath}"  scale="1.0 1.0 1.0"/>'
        body_mesh_xml += f'<geom mesh="{piece_name}" name="object_collisionn_{i}" class="collision"/>'
    
    # Write MJCF file
    model_xml = XML_TEMPLATE.replace("<object_mesh_to_replace></object_mesh_to_replace>",asset_mesh_xml)
    model_xml = model_xml.replace("<object_body_to_replace></object_body_to_replace>",body_mesh_xml)
    with open(output_path, 'w') as f:
        f.write(model_xml)
        
    return 

@task_wrapper
def remove_input(config):
    pass


XML_TEMPLATE = """<mujoco model="scene">
    <!-- <compiler angle="radian" meshdir="assets" autolimits="true"/> -->
    
    <option cone="elliptic" impratio="10"/>
    <statistic center="0.4 0 0.4" extent="1"/>
    <compiler autolimits="true" angle="radian"/>
    <option impratio="10" integrator="implicitfast" cone="elliptic" noslip_iterations="2"/>
    
    <default>
        <default class="visual">
        <geom group="2" type="mesh" contype="0" conaffinity="0"/>
        </default>
        <default class="collision">
        <geom group="3" type="mesh"/>
        </default>
    </default>
    
    <visual>
        <headlight diffuse="0.6 0.6 0.6" ambient="0.1 0.1 0.1" specular="0 0 0"/>
        <rgba haze="0.15 0.25 0.35 1"/>
        <global azimuth="120" elevation="-20"/>
    </visual>
    
    <asset>
        <object_mesh_to_replace></object_mesh_to_replace>
        <material name="black" specular="0.5" shininess="0.25" rgba="0.16355 0.16355 0.16355 1"/>
        <texture type="skybox" builtin="gradient" rgb1="0.3 0.5 0.7" rgb2="0 0 0" width="512" height="3072"/>
        <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"
        markrgb="0.8 0.8 0.8" width="300" height="300"/>
        <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>
    </asset>
    
    <worldbody>
        <light name="spotlight1" mode="targetbodycom" target="decomposed" pos="0 -1 2"/>
        <camera name="closeup1" pos="0.5 0.25 1.3" xyaxes="-1 0 0 0 -0.6 0.8"/>
        <camera name="closeup2" pos="0.5 0.0 0.8" xyaxes="1 0 0 0 -1 0"/>
        <camera name="closeup3" pos="0.1 0 1.05" xyaxes="0 -1 0 0 0 1"/>
        <camera name="closeup4"  pos="0.5 0 1.4" xyaxes="0 -1 0 1 0 0"/>
        <camera name="closeup5"  pos="0 -0.3 0.1" xyaxes="1 0 0 0 0 1"/>
        <camera name="closeup" pos="0  -0.3 0.1" xyaxes="1 0 0 0 0 1"/>
        <geom name="floor" size="0 0 0.05" type="plane" material="groundplane"/>
        <body name="decomposed" quat="1 0 0 1" pos="0 0 0">
        <freejoint/>
        <object_body_to_replace></object_body_to_replace>
        </body>
    </worldbody>
    <keyframe>
        <key name="home" qpos="0 0 0.8 1 0 0 0"/>
    </keyframe>
    </mujoco>"""