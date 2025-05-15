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
def export_tabletop_scene_cfg(config):
    (
        input_path,
        output_path,
        obj_id,
        info_path,
        file_path,
        xml_path,
        urdf_path,
        scale_lst,
        pose_cfg,
    ) = (
        config["input_path"],
        config["output_path"],
        config["obj_id"],
        config["info_path"],
        config["file_path"],
        config["xml_path"],
        config["urdf_path"],
        config["scale_lst"],
        config["pose_cfg"],
    )
    pose_lst = load_json(input_path)

    for scale in scale_lst:
        scale_name = f"scale{str(int(scale*100)).zfill(3)}"
        for i, pose in enumerate(pose_lst):
            pose_name = f"pose{str(i).zfill(3)}"
            for j in range(pose_cfg["repeat"]):
                save_path = os.path.join(output_path, f"{scale_name}_{pose_name}_{j}")

                scaled_pose = np.array(pose)
                scaled_pose[:3] *= scale
                scaled_pose[:3] += np.array(pose_cfg["t"]) + np.array(
                    pose_cfg["noise"]
                ) * (np.random.rand(3) - 0.5)

                scene_cfg = {
                    "scene": {
                        obj_id: {
                            "type": "rigid_object",
                            "file_path": os.path.relpath(
                                file_path, os.path.dirname(save_path)
                            ),
                            "xml_path": os.path.relpath(
                                xml_path, os.path.dirname(save_path)
                            ),
                            "urdf_path": os.path.relpath(
                                urdf_path, os.path.dirname(save_path)
                            ),
                            "info_path": os.path.relpath(
                                info_path, os.path.dirname(save_path)
                            ),
                            "scale": np.array([scale, scale, scale]),
                            "pose": scaled_pose,
                        },
                        "table": {
                            "type": "plane",
                            "pose": np.array([0.0, 0, 0, 1, 0, 0, 0]),
                            "size": np.array([0.0, 0, 1]),
                        },
                    },
                    "scene_id": obj_id + save_path.split(obj_id)[1],
                    "task": {
                        "type": "slide",
                        "obj_name": obj_id,
                        "axis": np.array([0.0, 0, 1]),
                        "distance": 0.1,
                    },
                }
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                np.save(save_path, scene_cfg)

    return


@task_wrapper
def export_floating_scene_cfg(config):
    (
        input_path,
        output_path,
        obj_id,
        info_path,
        file_path,
        xml_path,
        urdf_path,
        scale_lst,
    ) = (
        config["input_path"],
        config["output_path"],
        config["obj_id"],
        config["info_path"],
        config["file_path"],
        config["xml_path"],
        config["urdf_path"],
        config["scale_lst"],
    )

    for scale in scale_lst:
        save_path = os.path.join(output_path, f"scale{str(int(scale*100)).zfill(3)}")
        scene_cfg = {
            "scene": {
                obj_id: {
                    "type": "rigid_object",
                    "file_path": os.path.relpath(file_path, os.path.dirname(save_path)),
                    "xml_path": os.path.relpath(xml_path, os.path.dirname(save_path)),
                    "urdf_path": os.path.relpath(urdf_path, os.path.dirname(save_path)),
                    "info_path": os.path.relpath(info_path, os.path.dirname(save_path)),
                    "scale": np.array([scale, scale, scale]),
                    "pose": np.array([0.0, 0, 0, 1, 0, 0, 0]),
                }
            },
            "scene_id": obj_id + save_path.split(obj_id)[1],
            "task": {
                "type": "force_closure",
                "obj_name": obj_id,
            },
        }
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        np.save(save_path, scene_cfg)
    return
