from typing import Dict, List
import os
import json
import logging

import yaml
from yaml import Loader


def load_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def write_json(data: Dict, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=1)
    return


def load_yaml(file_path) -> Dict:
    with open(file_path) as file_p:
        data = yaml.load(file_p, Loader=Loader)
    return data


def task_wrapper(func):
    def wrapper(cfg, skip, debug):
        # Missing input_path means the failure of the last task. Directly finish the process of this object
        if ("check_input" not in cfg or cfg["check_input"]) and not os.path.exists(
            cfg["input_path"]
        ):
            raise Exception(f"input_path {cfg['input_path']} does not exist")

        # Print info of execuable program for debug
        if "quiet" in cfg and debug:
            cfg["quiet"] = False

        if "output_path" in cfg and os.path.exists(cfg["output_path"]) and skip:
            logging.debug(
                f"Skip task {func.__name__}: output path already exist in {cfg['output_path']}"
            )
            output = None
        else:
            if "output_path" in cfg.keys():
                os.makedirs(os.path.dirname(cfg["output_path"]), exist_ok=True)
            output = func(cfg)
            logging.debug(f"Finish task {func.__name__}.")

        if (
            "delete_input" in cfg
            and cfg["delete_input"]
            and os.path.exists(cfg["input_path"])
        ):
            os.system(f"rm {cfg['input_path']}")

        return output

    return wrapper
