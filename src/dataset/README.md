# Download

## DexGraspNet
Download links: [PKU dist](https://disk.pku.edu.cn/anyshare/zh-cn/link/AA94E7804CC4E24551B2AE30C39A1275C1/F980E10128184A3BA8A16A14B0879737/5986E8B5750843FB8431CEC07532E6DB?_tb=none) 
```
cd MeshProcess/assets

# Download and unzip raw mesh data
wget -O DGN_obj_raw.zip https://diskasu.pku.edu.cn:10002/Bucket/bab1d452-c23b-4d03-b766-329261bcc4d6/F980E10128184A3BA8A16A14B0879737/4CF7CED5317544CFAAE67CE30E00ED64\?response-content-disposition\=attachment%3B%20filename%2A%3Dutf-8%27%27DGNObj%255fraw.zip\&AWSAccessKeyId\=ASE\&Expires\=1739863597\&Signature\=qQ793vvLf1EivzJ1MHLUSWcpgoQ%3d
unzip DGN_obj_raw.zip

# Download processed mesh data
wget -O DGN_obj_raw.zip https://diskasu.pku.edu.cn:10002/Bucket/bab1d452-c23b-4d03-b766-329261bcc4d6/F980E10128184A3BA8A16A14B0879737/4CF7CED5317544CFAAE67CE30E00ED64\?response-content-disposition\=attachment%3B%20filename%2A%3Dutf-8%27%27DGNObj%255fraw.zip\&AWSAccessKeyId\=ASE\&Expires\=1739863597\&Signature\=qQ793vvLf1EivzJ1MHLUSWcpgoQ%3d
unzip DGN_obj_raw.zip
```

Processing:
```

```

Description: The official repository of [DexGraspNet](https://github.com/PKU-EPIC/DexGraspNet) has only released their processed meshes, which doesn't satisfy our need. Therefore, we re-processed the raw meshes using this repository. The source of raw mesh data includes [ShapeNetCore](https://huggingface.co/datasets/ShapeNet/ShapeNetCore/tree/main), [ShapeNetSem](https://huggingface.co/datasets/ShapeNet/ShapeNetSem-archive), [MuJoCo_Sanned_Objects](https://github.com/kevinzakka/mujoco_scanned_objects/tree/main), and [DDG](https://gamma.umd.edu/researchdirections/grasping/differentiable_grasp_planner). Since DDG's data link is not valid anymore, we use the DDG's meshes released by DexGraspNet as the raw mesh for processing. 


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
