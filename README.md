# MeshProcess 

1. Installation.
```
conda create -n meshproc python=3.10    
conda activate meshproc
```


2. Data preparing. The mesh should be organized as following:
```
Folder
|- xxx.obj
|- xxxx.obj
...
|_ xxxxx.obj
```
The guidance for some popular datasets, e.g. objaverse, are provided in `dataset`. 


3. Run scipts.
```
python scripts/main.py -p ${YOUR_PATH}
```
