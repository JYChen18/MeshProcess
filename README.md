# MeshProcess 

## Dependence
1. The code is currently only tested on Linux Ubuntu.
2. [ACVD](https://github.com/valette/ACVD).
3. [CoACD](https://github.com/JYChen18/CoACD).

## Installation.
1. clone the code and create conda environments.
```
git submodule update --init --recursive 

conda create -n meshproc python=3.10    
conda activate meshproc
pip install trimesh
pip install hydra-core
pip install lxml
```

2. Build the third-party packages, [ACVD](https://github.com/valette/ACVD/tree/master?tab=readme-ov-file#simple-compilation-howto-under-linux).
and [CoACD](https://github.com/SarahWeiii/CoACD?tab=readme-ov-file#3-compile), according to the official repositories. For ACVD, here is a guidance for installing the [VTK](https://www.vtk.org/) dependence:
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

2. Data preparing. The mesh should be organized as in `example_data`.
The download guidance for some popular datasets, e.g. objaverse, are also provided in `src/dataset`. 


3. Run scipts for `example_data`. 
```
# processing meshes
python src/script/process.py data=example task=main

# Get statistic
python src/script/statistic.py data=example task=main

# remove processed results and only leave raw.obj
python src/script/process.py data=example task=clean

```

## TODO

1. Get xml for MuJoCo
2. Get valid object pose on a table from MuJoCo
3. GPU-based partial point clouds rendering 
4. (Potential) Reduce part number of the CoACD output
5. 

## Known issues
1. The output mesh of the OpenVDB for manifold repairing would be a little bit larger (~1%) than the input mesh.
