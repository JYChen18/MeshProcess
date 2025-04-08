import sys
import os
import trimesh
import numpy as np
import lxml.etree as et

from ..util_file import load_json, write_json, task_wrapper


# save basic info
@task_wrapper
def get_basic_info(config):
    input_path, output_path = config["input_path"], config["output_path"]
    tm_mesh = trimesh.load(input_path, force="mesh")
    obb_length = tm_mesh.bounding_box_oriented.primitive.extents
    gravity_center = tm_mesh.center_mass
    write_json(
        {
            "gravity_center": gravity_center.tolist(),
            "obb": obb_length.tolist(),
            "scale": 1.0,
            "density": tm_mesh.density,
            "mass": tm_mesh.mass,
        },
        output_path,
    )
    return


# save complete point cloud
@task_wrapper
def get_complete_pc(config):
    input_path, output_path, point_num = (
        config["input_path"],
        config["output_path"],
        config["point_num"],
    )
    tm_mesh = trimesh.load(input_path, force="mesh")
    complete_pc, _ = trimesh.sample.sample_surface(tm_mesh, point_num)
    np.save(output_path, complete_pc.astype(np.float16))
    return


@task_wrapper
def export_urdf(config):
    input_path, output_path = (
        config["input_path"],
        config["output_path"],
    )

    root = et.Element("robot", name="root")

    piece_names = os.listdir(input_path)
    commonprefix = os.path.commonprefix([input_path, output_path])

    prev_link_name = None
    for i, piece_name in enumerate(piece_names):
        piece_filename = os.path.join(input_path, piece_name).removeprefix(commonprefix)

        link_name = "link_{}".format(piece_name)
        # I = [["{:.2E}".format(y) for y in x] for x in piece.moment_inertia]  # NOQA
        link = et.SubElement(root, "link", name=link_name)
        inertial = et.SubElement(link, "inertial")
        et.SubElement(inertial, "origin", xyz="0 0 0", rpy="0 0 0")
        # et.SubElement(inertial, 'mass', value='{:.2E}'.format(piece.mass))
        # et.SubElement(
        #     inertial,
        #     "inertia",
        #     ixx=I[0][0],
        #     ixy=I[0][1],
        #     ixz=I[0][2],
        #     iyy=I[1][1],
        #     iyz=I[1][2],
        #     izz=I[2][2],
        # )

        # Visual Information
        visual = et.SubElement(link, "visual")
        et.SubElement(visual, "origin", xyz="0 0 0", rpy="0 0 0")
        geometry = et.SubElement(visual, "geometry")
        et.SubElement(geometry, "mesh", filename=piece_filename, scale="1.0 1.0 1.0")

        # Collision Information
        collision = et.SubElement(link, "collision")
        et.SubElement(collision, "origin", xyz="0 0 0", rpy="0 0 0")
        geometry = et.SubElement(collision, "geometry")
        et.SubElement(geometry, "mesh", filename=piece_filename, scale="1.0 1.0 1.0")

        # Create rigid joint to previous link
        if prev_link_name is not None:
            joint_name = "{}_joint".format(link_name)
            joint = et.SubElement(root, "joint", name=joint_name, type="fixed")
            et.SubElement(joint, "origin", xyz="0 0 0", rpy="0 0 0")
            et.SubElement(joint, "parent", link=prev_link_name)
            et.SubElement(joint, "child", link=link_name)

        prev_link_name = link_name

    # Write URDF file
    tree = et.ElementTree(root)
    tree.write(output_path, pretty_print=True)

    return


@task_wrapper
def remove_input(config):
    pass


@task_wrapper
def export_scene_cfg(config):
    input_path, output_path, obj_id, file_path, xml_path, urdf_path, scale_lst = (
        config["input_path"],
        config["output_path"],
        config["obj_id"],
        config["file_path"],
        config["xml_path"],
        config["urdf_path"],
        config["scale_lst"],
    )
    pose_lst = load_json(input_path)

    for scale in scale_lst:
        save_path = os.path.join(
            os.path.dirname(output_path),
            "floating",
            f"scale{str(int(scale*100)).zfill(3)}",
        )
        scene_cfg = {
            "scene": {
                obj_id: {
                    "type": "rigid_mesh",
                    "file_path": os.path.relpath(file_path, os.path.dirname(save_path)),
                    "xml_path": os.path.relpath(xml_path, os.path.dirname(save_path)),
                    "urdf_path": os.path.relpath(urdf_path, os.path.dirname(save_path)),
                    "scale": np.array([scale, scale, scale]),
                    "pose": np.array([0.0, 0, 0, 1, 0, 0, 0]),
                    "pose_id": -1,
                }
            },
            "scene_id": f"floating_{obj_id}_scale{str(int(scale*100)).zfill(3)}",
            "interest_obj_name": obj_id,
            "interest_direction": np.array([0.0, 0, 1, 0, 0, 0]),
        }
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        np.save(save_path, scene_cfg)

        scene_cfg["scene"]["table"] = {
            "type": "plane",
            "pose": np.array([0.0, 0, 0, 1, 0, 0, 0]),
            "size": np.array([0.0, 0, 1]),
        }

        for i, pose in enumerate(pose_lst):
            scaled_pose = np.array(pose)
            scaled_pose[:3] *= scale
            scene_cfg["scene"][obj_id]["pose"] = scaled_pose
            scene_cfg["scene"][obj_id]["pose_id"] = i
            scene_cfg["scene_id"] = (
                f"tabletop_{obj_id}_pose{str(i).zfill(3)}_scale{str(int(scale*100)).zfill(3)}"
            )

            save_path2 = os.path.join(
                os.path.dirname(output_path),
                "tabletop",
                f"pose{str(i).zfill(3)}_scale{str(int(scale*100)).zfill(3)}",
            )
            os.makedirs(os.path.dirname(save_path2), exist_ok=True)
            np.save(save_path2, scene_cfg)
    return
