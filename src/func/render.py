import os
import sys
import logging
import multiprocessing
from glob import glob
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util.warp_render import batch_warp_render
from util.util_file import load_json


def func_render(cfg):
    assert (
        "**" in cfg.data.input_template
        and len(cfg.data.input_template.split("**")) == 2
    )

    gpu_lst = list(cfg.func.gpu_lst) * cfg.func.thread_per_gpu
    all_scene_lst = glob(cfg.func.scene_cfg_path, recursive=True)
    all_scene_num = len(all_scene_lst)
    scene_num_lst = np.array([all_scene_num // len(gpu_lst)] * len(gpu_lst))
    scene_num_lst[: (all_scene_num % len(gpu_lst))] += 1
    assert scene_num_lst.sum() == all_scene_num

    logging.info("#" * 30)
    logging.info(f"Input template: {cfg.data['input_template']}")
    logging.info(f"Output template: {cfg.data['output_vision_template']}")
    logging.info(f"Object Number: {all_scene_num}")
    logging.info(
        f"Task: Rendering point cloud({cfg.func.save_pc}), depth image({cfg.func.save_depth}), rgb image({cfg.func.save_rgb})"
    )
    logging.info("#" * 30)

    if cfg.debug_id is not None:
        batch_warp_render(cfg, [cfg.debug_id], cfg.func.gpu_lst[0])
    else:
        p_list = []
        for i, gpu_id in enumerate(gpu_lst):
            start = (scene_num_lst[:i]).sum()
            end = (scene_num_lst[: (i + 1)]).sum()
            p = multiprocessing.Process(
                target=batch_warp_render,
                args=(cfg, all_scene_lst[start:end], gpu_id),
            )
            p.start()
            p_list.append(p)

        for p in p_list:
            p.join()
    return
