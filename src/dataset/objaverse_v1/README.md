# Download objaverse 1.0

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
