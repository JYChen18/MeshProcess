import os
import sys
from copy import deepcopy
import logging
import traceback
import multiprocessing
import glob
from omegaconf import open_dict

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util.proc.mesh import *
from util.proc.basic import *
from util.proc.tabletop_pose import *


def process_single_obj(params):
    cfg, obj_id = params
    # read config
    new_task_cfg = deepcopy(cfg["task"])
    for task_name, task_cfg in new_task_cfg.items():
        real_task_name = task_name.split("-")[-1]
        with open_dict(task_cfg):
            task_cfg.obj_id = obj_id
        for k, v in task_cfg.items():
            if k.endswith("_path"):
                task_cfg[k] = os.path.abspath(v.replace("**", obj_id))
        try:
            eval(real_task_name)(
                task_cfg,
                skip=cfg["skip"],
                debug=cfg["debug_id"] is not None,
            )
        except Exception as e:
            error_traceback = traceback.format_exc()
            logging.info(
                f"Failure! Task: {task_name}, obj: {obj_id} \n {error_traceback}"
            )
            return
    logging.info(f"Success! obj: {obj_id}")
    return


def func_proc(cfg):
    assert (
        "**" in cfg["data"]["input_template"]
        and len(cfg["data"]["input_template"].split("**")) == 2
    )
    full_path_lst = glob.glob(cfg["data"]["input_template"])
    prefix = cfg["data"]["input_template"].split("**")[0]
    suffix = cfg["data"]["input_template"].split("**")[1]
    obj_lst = [p.replace(prefix, "").replace(suffix, "") for p in full_path_lst]

    logging.info("#" * 30)
    logging.info(f"Input template: {cfg['data']['input_template']}")
    logging.info(f"Output template: {cfg['data']['output_template']}")
    logging.info(f"Object Number: {len(obj_lst)}")
    logging.info(f"Tasks: {list(cfg['task'].keys())}")
    logging.info("#" * 30)

    if cfg["debug_id"] is not None:
        process_single_obj((cfg, cfg["debug_id"]))
    else:
        iterable_params = [(cfg, obj_id) for obj_id in obj_lst]
        with multiprocessing.Pool(processes=cfg["n_worker"]) as pool:
            result_iter = pool.imap_unordered(process_single_obj, iterable_params)
            results = list(result_iter)
    return
