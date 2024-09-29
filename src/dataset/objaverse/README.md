# Download objaverse 1.0

1. Installation
```
conda activate meshproc
pip install objaverse --upgrade --quiet
pip install tqdm
```

2. Change the root path in `src/config/data/objaverse.yaml`.

3. Download the subset according to the category annotation provided in [GObjaverse](https://aigc3d.github.io/gobjaverse/).
```
python robust_download.py -c Daily-Used
```

4. Save .obj file to a new folder.
```
python glb2obj.py
```
