import os
import sys
from copy import deepcopy

import mujoco
import numpy as np
import imageio

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.sample import even_sample_points_on_sphere
from utils.util_file import task_wrapper
from utils.rotation import batched_quat_delta


def remove_duplicated_pose(pose_array):
    delta_angle, delta_axis = batched_quat_delta(
        pose_array[:, None, 3:], pose_array[None, :, 3:]
    )
    z_axis_duplicated = (
        (np.linalg.norm(delta_axis - np.array([[[0, 0, 1]]]), axis=-1) < 0.1)
        | (np.linalg.norm(delta_axis - np.array([[[0, 0, -1]]]), axis=-1) < 0.1)
        | (delta_angle < 0.01)
    )

    d1, d2 = np.where(z_axis_duplicated)
    remove_ids = [max(i1, i2) for i1, i2 in zip(d1, d2) if i1 != i2]
    remain_ids = [i for i in range(pose_array.shape[0]) if i not in remove_ids]
    final_pose_array = pose_array[remain_ids]

    return final_pose_array


@task_wrapper
def get_tabletop_pose(config):
    input_path, output_path, max_try_num, remove_duplicated, debug_vis_path = (
        config["input_path"],
        config["output_path"],
        config["max_try_num"],
        config["remove_duplicated"],
        config["debug_vis_path"] if "debug_vis_path" in config else None,
    )

    with open(input_path, "r") as file:
        model_xml = file.read()
    model_xml = model_xml.replace(
        'meshdir="."', f'meshdir="{os.path.dirname(input_path)}"'
    )

    # Use scale = 0.1 to simulate to reduce random error.
    scale = 0.1
    model_xml = model_xml.replace(
        'scale="1.0 1.0 1.0"', f'scale="{scale} {scale} {scale}"'
    )

    model = mujoco.MjModel.from_xml_string(model_xml)
    model.geom_friction = np.array([0.6, 0.02, 0.0001])
    model.opt.timestep = 0.005
    data = mujoco.MjData(model)

    if debug_vis_path is not None:
        renderer = mujoco.Renderer(model, 480, 640)

    # Initialize object pose
    obj_trans = np.array([[0.0, 0, scale * 1.2]]).repeat(max_try_num, axis=0)
    random_obj_quat = even_sample_points_on_sphere(4, delta_angle=45)
    random_choice = np.random.permutation(random_obj_quat.shape[0])[:max_try_num]
    random_obj_pose = np.concatenate(
        [obj_trans, random_obj_quat[random_choice]], axis=-1
    )

    pose_lst = []
    for pose_id in range(max_try_num):
        mujoco.mj_resetDataKeyframe(model, data, 0)
        data.qpos = deepcopy(random_obj_pose[pose_id])
        data.qvel = 0
        mujoco.mj_forward(model, data)

        # Start to simulate
        frames = []
        for i in range(800):
            mujoco.mj_step(model, data)

            if debug_vis_path is not None and i % 20 == 0:
                renderer.update_scene(data, "closeup")
                pixels = renderer.render()
                frames.append(pixels)

        final_object_qpos = deepcopy(data.qpos)

        # Check success or not
        succ_flag = True
        for i in range(1):
            mujoco.mj_resetDataKeyframe(model, data, 0)
            data.qpos = deepcopy(final_object_qpos)
            data.qvel = 0
            for j in range(200):
                mujoco.mj_step(model, data)
                if debug_vis_path is not None and j % 50 == 0:
                    renderer.update_scene(data, "closeup")
                    pixels = renderer.render()
                    frames.append(pixels)
            delta_angle, _ = batched_quat_delta(data.qpos[3:], final_object_qpos[3:])
            delta_trans = np.linalg.norm(data.qpos[:3] - final_object_qpos[:3])
            if delta_trans > 0.001 or np.degrees(delta_angle) > 1:
                succ_flag = False

        if succ_flag:
            pose_lst.append(final_object_qpos)

        if debug_vis_path is not None:
            save_path = debug_vis_path.replace(".gif", f"_{succ_flag}_{pose_id}.gif")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            imageio.mimsave(save_path, frames, fps=10)

    # post-process
    if len(pose_lst) > 0:
        pose_array = np.array(pose_lst)
        pose_array[..., :2] = 0
        pose_array[..., 2] *= 1 / scale  # Save the corresponding pose of scale = 1.0.
        if remove_duplicated:
            pose_array = remove_duplicated_pose(pose_array)
        np.save(output_path, pose_array)

    return
