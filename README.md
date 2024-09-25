# MeshProcess 

1. Installation.
```
conda create -n meshproc python=3.10    
conda activate meshproc
pip install coacd
pip install scipy
pip install lxml
```


2. Data preparing. The mesh should be organized as following:
```
folder
|- abc.obj
|- def.obj
...
|_ xyz.obj
```
The guidance for some popular datasets, e.g. objaverse, are provided in `dataset`. 


3. Run scipts.
```
python src/preprocess.py -f ${YOUR_FOLDER}
```


## Acknowledgement

This work is built on many amazing research works and open-source projects:
1. [ManifoldPlus](https://github.com/hjwdzh/ManifoldPlus)
2. [CoACD](https://github.com/SarahWeiii/CoACD)
3. [Trimesh](https://github.com/mikedh/trimesh)
4. [Objaverse](https://objaverse.allenai.org/)

Thanks for their excellent work and great contribution.
