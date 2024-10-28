from pytorch3d import loss as py3l
import json
import glob
import tqdm
import torch
import os
import numpy as np
import math

with open("obb_splits", "r") as f:
    obb_split = json.load(f)
split_num = 20
bin_length = 2 / split_num

folder = "/mnt/disk0/objaverse/hf-objaverse-v1/processed_data"
info_lst = glob.glob(os.path.join(folder, "**", "info/simplified.json"))

for info_path in tqdm.tqdm(info_lst):
    obj_id = info_path.replace(folder + "/", "").replace("/info/simplified.json", "")
    npy_path = info_path.replace("info/simplified.json", "point_clouds/complete.npy")
    pc = torch.tensor(np.load(npy_path)[np.random.permutation(4096)[:512]]).unsqueeze(0)

    with open(info_path, "r") as f:
        info = json.load(f)
    obb = info["obb"]

    similar_lst = None
    for i in range(3):
        group_id = min(math.floor(obb[i] / bin_length), split_num - 1)
        a, b, c = (
            obb_split[i][group_id],
            obb_split[i][min(group_id + 1, split_num - 1)],
            obb_split[i][max(group_id - 1, 0)],
        )
        curr_set = (set(a).union(set(b))).union(set(c))
        if similar_lst is None:
            similar_lst = curr_set
        else:
            similar_lst = similar_lst.intersection(curr_set)
    similar_lst = list(similar_lst)

    similar_pc = []
    for similar_obj in similar_lst:
        new_npy_path = npy_path.replace(obj_id, similar_obj)
        if os.path.exists(new_npy_path):
            new_pc = np.load(new_npy_path)[np.random.permutation(4096)[:512]]
            # TODO: pose transformation with obb info
            similar_pc.append(new_pc)
    if len(similar_pc) == 0:
        continue
    similar_pc = torch.tensor(np.stack(similar_pc))
    print(similar_pc.shape)
    cd, _ = py3l.chamfer_distance(
        pc.expand_as(similar_pc).float().to("cuda:0"),
        similar_pc.float().to("cuda:0"),
        batch_reduction=None,
    )
    aa = cd.min() < 0.01
    print(cd.max(), cd.min(), cd.mean())
    import pdb

    pdb.set_trace()
