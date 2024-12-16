import glob
import os

obj_folder = "/mnt/disk1/jiayichen/data/DGNObj"
pc_lst = glob.glob(os.path.join(obj_folder, "**/point_clouds/table_pc"))
print(f"Find {len(pc_lst)} pc folder, remove them")
for i in pc_lst:
    os.system(f"rm -r {i}")
