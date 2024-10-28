from glob import glob
import hydra
import logging
import os
import sys

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.util_file import write_json

logger = logging.getLogger("DataSplit")


@hydra.main(config_path="../config", config_name="base", version_base=None)
def main(cfg):
    full_path_lst = glob(cfg["data"]["input_template"])
    prefix = cfg["data"]["input_template"].split("**")[0]
    suffix = cfg["data"]["input_template"].split("**")[1]
    valid_obj_lst = set(
        [p.replace(prefix, "").replace(suffix, "") for p in full_path_lst]
    )
    total_valid_obj_num = len(valid_obj_lst)

    for task_name, task_cfg in cfg["task"].items():
        if "output_path" in task_cfg:
            curr_path_lst = glob(task_cfg["output_path"])
            prefix = task_cfg["output_path"].split("**")[0]
            suffix = task_cfg["output_path"].split("**")[1]
            curr_valid_obj_lst = set(
                [p.replace(prefix, "").replace(suffix, "") for p in curr_path_lst]
            )

            if len(curr_valid_obj_lst) / len(valid_obj_lst) < 0.1:
                print(f"Skipped file suffix: {suffix[1:]}")
                continue

            print(f"Checked file suffix: {suffix[1:]}")
            valid_obj_lst = valid_obj_lst.intersection(curr_valid_obj_lst)

    valid_obj_num = len(valid_obj_lst)
    print(
        "Valid object number: %d; Total object number: %d"
        % (valid_obj_num, total_valid_obj_num)
    )
    shuffled_obj_lst = np.array(list(valid_obj_lst))[
        np.random.permutation(valid_obj_num)
    ]
    train_obj_lst = shuffled_obj_lst[: int(valid_obj_num * 0.8)]
    test_obj_lst = shuffled_obj_lst[int(valid_obj_num * 0.8) :]
    os.makedirs(cfg["data"]["output_split"], exist_ok=not cfg["skip"])
    write_json(
        list(train_obj_lst), os.path.join(cfg["data"]["output_split"], "train.json")
    )
    write_json(
        list(test_obj_lst), os.path.join(cfg["data"]["output_split"], "test.json")
    )
    write_json(
        list(shuffled_obj_lst), os.path.join(cfg["data"]["output_split"], "all.json")
    )
    return


if __name__ == "__main__":
    main()
