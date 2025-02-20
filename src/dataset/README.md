# Dataset Download
Here is the guides to download object assets used in [BODex](https://pku-epic.github.io/BODex/) and [follow-up work](todo). BODex only evaluates on a part of the objects from DexGraspNet.

## DexGraspNet
Download links: [PKU dist](https://disk.pku.edu.cn/anyshare/zh-cn/link/AA94E7804CC4E24551B2AE30C39A1275C1/F980E10128184A3BA8A16A14B0879737/5986E8B5750843FB8431CEC07532E6DB?_tb=none) 

- Downloading and unzip processed results: `DGN_obj_processed.zip`, `DGN_obj_split.zip`, and (optionally) `DGN_obj_vision.zip`. The final folder should be organized like:
```
assets/object/DGN_obj
|- processed_data
|  |- core_bottle_1a7ba1f4c892e2da30711cdbdbc73924
|  |_ ...
|- valid_split
|  |- all.json
|  |_ ...
|_ vision_data (not necessary for grasp synthesis and only needed for network learning)
|  |- core_bottle_1a7ba1f4c892e2da30711cdbdbc73924
|  |_ ...
```

- (Alternatively) Downloading raw meshes `DGN_obj_raw.zip` and processing by yourself according to the [guides](https://github.com/JYChen18/MeshProcess/tree/main?tab=readme-ov-file#running-seperately). Note that if processed by yourself, the resulted meshes and splits may slightly differ from ours.

- Discussion: The official repository of [DexGraspNet](https://github.com/PKU-EPIC/DexGraspNet) has only released their processed meshes, which doesn't satisfy our need. Therefore, we re-processed the raw meshes using this repository. The source of raw mesh data includes [ShapeNetCore](https://huggingface.co/datasets/ShapeNet/ShapeNetCore/tree/main), [ShapeNetSem](https://huggingface.co/datasets/ShapeNet/ShapeNetSem-archive), [MuJoCo_Sanned_Objects](https://github.com/kevinzakka/mujoco_scanned_objects/tree/main), and [DDG](https://gamma.umd.edu/researchdirections/grasping/differentiable_grasp_planner). Since DDG's data link is not valid anymore, we use the DDG's meshes released by DexGraspNet as the raw mesh for processing. 


## Objaverse 1.0

1. Installation
```
conda activate meshproc
pip install objaverse --upgrade --quiet
pip install tqdm
```

2. Create soft link to change the dataset path for downloading. By default, the dataset will be downloaded to `~/.objaverse`. 

```
ln -s ${YOUR_PATH} ~/.objaverse
```

3. Download the subset according to the category annotation provided in [GObjaverse](https://aigc3d.github.io/gobjaverse/).
```
python robust_download.py -c Daily-Used
```

4. Organize the object folder by soft links.
```
python organize.py
```
