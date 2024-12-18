# MeshProcess 

## Highlights
1. Generates simplified 2-manifold meshes with convex decomposition *in seconds*.
2. High success rate on messy, in-the-wild mesh data, including datasets like [Objaverse](https://objaverse.allenai.org).
3. Supports parallel processing of multiple meshes on CPUs.
4. Easy to customize the processing tasks.

## Dependences
1. The code is currently only tested on Linux Ubuntu.
2. [ACVD](https://github.com/valette/ACVD) for mesh simplification.
3. [CoACD](https://github.com/JYChen18/CoACD) for convex decomposition.
4. [OpenVDB](https://www.openvdb.org/) for generating a 2-manifold mesh.

## Installation
1. Clone the third-parties.
```
git submodule update --init --recursive 
```

2. Create and install the python environment using [Conda](https://docs.anaconda.com/miniconda/).
```
conda create -n meshproc python=3.10    
conda activate meshproc
pip install trimesh
pip install hydra-core
pip install lxml

# For offline partial point cloud rendering
pip install warp-lang
pip install opencv-python
pip install pyglet
```

3. Build the third-party packages according to the guidance in [ACVD](https://github.com/valette/ACVD/tree/master?tab=readme-ov-file#simple-compilation-howto-under-linux)
and [CoACD](https://github.com/SarahWeiii/CoACD?tab=readme-ov-file#3-compile). OpenVDB will be installed automatically in CoACD. For ACVD, here is a guidance for installing the [VTK](https://www.vtk.org/) dependence:
```
sudo apt-get update
sudo apt install -y build-essential cmake git unzip qt5-default libqt5opengl5-dev libqt5x11extras5-dev libeigen3-dev libboost-all-dev libglew-dev libglvnd-dev

git clone https://gitlab.kitware.com/vtk/vtk.git
cd vtk
git checkout v9.2.0     
mkdir build
cd build
cmake ..
make -j12
sudo make install
export VTK_DIR=/usr/local/include/vtk-9.2
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
``` 

## Mesh Data Preparing
1. The meshes should be organized similarly as in `example_data`. 

2. The downloading guidance for [objaverse-1.0](https://objaverse.allenai.org/objaverse-1.0/) is in `src/dataset/objaverse_v1/README.md`.

## Running
1. Processing meshes for `example_data`. The processed results will be saved in `example_data/output` and the logs will be saved to `outputs`.
```
python src/script/process.py data=example task=main
# python src/script/process.py data=example task=simplified
```
2. Get statistic.
```
python src/script/statistic.py data=example task=main
```

3. Rendering partial point cloud.
```
python src/script/multi_gpu_render.py
```

