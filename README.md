# MeshProcess 

This repository **does not propose any new methods**, but provides easy-to-use code that leverages advanced tools for efficiently preparing large-scale, high-quality 3D mesh assets.

## Introduction

### Main Features 
- Generate simplified 2-manifold meshes using [OpenVDB](https://www.openvdb.org/) and [ACVD](https://github.com/valette/ACVD).
- Perform convex decomposition with [CoACD](https://github.com/JYChen18/CoACD).
- Render single-view point clouds using [Warp](https://github.com/NVIDIA/warp).

### Highlights
1. **Fast**: Processes each mesh in seconds, with parallel processing support for multiple meshes.
2. **Robust**: Achieves over 95% success rate for processing messy mesh data, including datasets like [Objaverse](https://objaverse.allenai.org).
3. **Easy to Use**: Customizable processing tasks that can be executed with a single command.

### Projects Using MeshProcess
- [BODex: Scalable and Efficient Robotic Dexterous Grasp Synthesis Using Bilevel Optimization](https://pku-epic.github.io/BODex/), by Jiayi Chen*, Yubin Ke*, and He Wang. ICRA 2025.

## Getting Started
### Installation
1. Clone the third-party dependencies.
```
git submodule update --init --recursive --progress
```

2. Create and set up the Python environment using [Conda](https://docs.anaconda.com/miniconda/).
```
conda create -n meshproc python=3.10    
conda activate meshproc
pip install mujoco
pip install trimesh
pip install hydra-core
pip install lxml

# For partial point cloud rendering
pip install warp-lang
pip install opencv-python
pip install pyglet
```

3. Build the third-party package ACVD following their [installation guide](https://github.com/valette/ACVD/tree/master?tab=readme-ov-file#simple-compilation-howto-under-linux). To install the [VTK](https://www.vtk.org/) dependencies of ACVD,
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

4. Build our customized CoACD by following the [compiling instructions](https://github.com/JYChen18/CoACD?tab=readme-ov-file#3-compile). Please note that we do not support CoACD installed via `pip`. OpenVDB will be automatically included after compiling CoACD.


### Running
1. **Processing meshes**: For a quick start, example mesh data is provided in the `assets/example_obj/raw_mesh` directory. Processed results will be saved in `assets/example_obj/processed_data`.
```
python src/main.py func=proc
```

2. **(Optional) Getting statistics**: This can be used to monitor the progress during processing meshes.
```
python src/main.py func=stat
```

3. **Recording and spliting valid data**: The result will be saved in `assets/example_obj/valid_split`. 
```
python src/main.py func=split
```

4. **Rendering partial point cloud and (optional) images**: The result will be saved in `assets/example_obj/vision_data`. 
```
python src/main.py func=render
```

### Dataset Downloads
Our code has also been tested on object assets from [DexGraspNet](https://pku-epic.github.io/DexGraspNet/) and [Objaverse](https://objaverse.allenai.org/objaverse-1.0). Please see the guides [here]() for downloading and processing.

## Citation
If you found this repository useful, please consider to cite the following works:
- Our paper: 
```
@article{chen2024bodex,
title={BODex: Scalable and Efficient Robotic Dexterous Grasp Synthesis Using Bilevel Optimization},
author={Chen, Jiayi and Ke, Yubin and Wang, He},
journal={arXiv preprint arXiv:2412.16490},
year={2024}
}
```
- [CoACD](https://github.com/SarahWeiii/CoACD) for convex decomposition:
```
@article{wei2022coacd,
  title={Approximate convex decomposition for 3d meshes with collision-aware concavity and tree search},
  author={Wei, Xinyue and Liu, Minghua and Ling, Zhan and Su, Hao},
  journal={ACM Transactions on Graphics (TOG)},
  volume={41},
  number={4},
  pages={1--18},
  year={2022},
  publisher={ACM New York, NY, USA}
}
```
- [ACVD](https://github.com/valette/ACVD) for mesh simplification:
```
@article{valette2008generic,
  title={Generic remeshing of 3D triangular meshes with metric-dependent discrete Voronoi diagrams},
  author={Valette, S{\'e}bastien and Chassery, Jean Marc and Prost, R{\'e}my},
  journal={IEEE Transactions on Visualization and Computer Graphics},
  volume={14},
  number={2},
  pages={369--381},
  year={2008},
  publisher={IEEE}
}
```
