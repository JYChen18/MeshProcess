from glob import glob
import logging


def func_stat(cfg):
    all_valid_obj_num = len(glob(cfg["data"]["input_template"]))
    prev_valid_obj_num = all_valid_obj_num
    task_lst = []
    for task_name, task_cfg in cfg["task"].items():
        if "output_path" in task_cfg:
            task_lst.append(task_name)
            curr_valid_obj_num = len(glob(task_cfg["output_path"]))
            if curr_valid_obj_num / prev_valid_obj_num > 0.1:
                logging.info(
                    "Success rate of %s: %.4f"
                    % (task_lst, curr_valid_obj_num / prev_valid_obj_num)
                )
                task_lst = []
                prev_valid_obj_num = curr_valid_obj_num

    logging.info(
        "Valid object number: %d; Total success rate: %.4f"
        % (curr_valid_obj_num, curr_valid_obj_num / all_valid_obj_num)
    )
    return
