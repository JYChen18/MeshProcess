import numpy as np
import json
import glob
import os
import tqdm
import math

split_num = 20
bin = np.linspace(0, 2, split_num)
bin_length = 2 / split_num
obb_split = []
for i in range(3):
    tmp = []
    for j in range(split_num):
        tmp.append(list())
    obb_split.append(tmp)

folder = "/mnt/disk0/objaverse/hf-objaverse-v1/processed_data"
info_lst = glob.glob(os.path.join(folder, "**", "info/simplified.json"))
for info_path in tqdm.tqdm(info_lst):
    obj_id = info_path.replace(folder + "/", "").replace("/info/simplified.json", "")
    with open(info_path, "r") as f:
        info = json.load(f)
    obb = info["obb"]
    for i in range(3):
        group_id = min(math.floor(obb[i] / bin_length), split_num - 1)
        obb_split[i][group_id].append(obj_id)

with open("obb_splits", "w") as file:
    json.dump(obb_split, file, indent=1)
