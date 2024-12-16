import argparse
import multiprocessing
import subprocess
import os
import numpy as np
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.util_file import load_json


def worker(gpu_id, folder, split_path, start, end, output_path):
    with open(output_path, "w") as output_file:
        print(
            f"python src/proc/render.py -f {folder} -sp {split_path} -g {gpu_id} -s {start} -e {end}"
        )
        subprocess.call(
            f"python src/proc/render.py -f {folder} -sp {split_path} -g {gpu_id} -s {start} -e {end}",
            shell=True,
            stdout=output_file,
            stderr=output_file,
        )
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--data_folder",
        type=str,
        default="/mnt/disk1/jiayichen/data/DGNObj",
        help="the path to the data directory",
    )
    parser.add_argument(
        "-sp",
        "--split_path",
        type=str,
        default="/mnt/disk1/jiayichen/data/DGNObj_splits/all.json",
        help="the path to the data directory",
    )
    parser.add_argument(
        "-n", "--number", type=int, default=10, help="number on each gpu"
    )
    parser.add_argument("-g", "--gpu", nargs="+", required=True, help="gpu id list")
    args = parser.parse_args()

    gpu_lst = args.gpu * args.number

    all_obj_num = len(load_json(args.split_path))
    obj_num_lst = np.array([all_obj_num // len(gpu_lst)] * len(gpu_lst))
    obj_num_lst[: (all_obj_num % len(gpu_lst))] += 1
    assert obj_num_lst.sum() == all_obj_num

    p_list = []
    for i, gpu_id in enumerate(gpu_lst):
        start = (obj_num_lst[:i]).sum()
        end = (obj_num_lst[: (i + 1)]).sum()

        os.makedirs("debug", exist_ok=True)
        output_path = f"debug/render{i}.txt"
        p = multiprocessing.Process(
            target=worker,
            args=(gpu_id, args.data_folder, args.split_path, start, end, output_path),
        )
        p.start()
        print(f"create process :{p.pid}")
        p_list.append(p)

    for p in p_list:
        p.join()
