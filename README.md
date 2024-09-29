# MeshProcess 

1. Installation.
```
conda create -n meshproc python=3.10    
conda activate meshproc
```

To install the third-party repositories, see the compiling guidance in [ACVD](https://github.com/valette/ACVD/tree/master?tab=readme-ov-file#simple-compilation-howto-under-linux) and [CoACD](https://github.com/SarahWeiii/CoACD?tab=readme-ov-file#3-compile). 
```
git submodule update --init --recursive 
```

Detailed guidance for installing the VTK dependence for ACVD:
```
sudo apt-get update
sudo apt install -y build-essential cmake git unzip qt5-default libqt5opengl5-dev libqt5x11extras5-dev libeigen3-dev libboost-all-dev libglew-dev libglvnd-dev

git clone https://gitlab.kitware.com/vtk/vtk.git
cd vtk
git checkout v9.2.0     
mkdir build
cd build
cmake ..
make
sudo make install
export VTK_DIR=/usr/local/include/vtk-9.2
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
``` 

2. Data preparing. The mesh should be organized as in `example_data`:
```
folder
|- abcdefg # object id
    |_mesh
        |_raw.obj
|- bcdefgh  # object id
...
|_ qwertyu
```
The download guidance for some popular datasets, e.g. objaverse, are also provided in `src/dataset`. 


3. Run scipts for `example_data`. 
```
# processing meshes
python src/script/process.py task=main

# remove processed results and only leave raw.obj
python src/script/process.py task=clean

```

## TODO

1. Get xml for MuJoCo
2. Get valid object pose on a table from MuJoCo
3. GPU-based partial point clouds rendering 
4. (Potential) Reduce part number of the CoACD output
5. 

## Known issues
1. The simplified mesh would be a little bit larger than the original mesh.


## Acknowledgement

This work is built on many amazing research works and open-source softwares:
1. [ACVD](https://github.com/valette/ACVD)
2. [CoACD](https://github.com/SarahWeiii/CoACD)
3. [OpenVDB](https://www.openvdb.org/)
4. [Trimesh](https://github.com/mikedh/trimesh)
5. [Objaverse](https://objaverse.allenai.org/)

Thanks for their excellent work and great contribution.
