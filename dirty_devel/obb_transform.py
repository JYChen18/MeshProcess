import trimesh
import numpy as np

path = "/mnt/disk1/jiayichen/code/MeshProcess/example_data/output/e9e567517b434ebd9890c52edfe4eed9/mesh/simplified.obj"
tm_mesh = trimesh.load(path)
print(tm_mesh.bounding_box_oriented.primitive.extents)
obb_transform = tm_mesh.bounding_box_oriented.primitive.transform
print(obb_transform)
np_path = "/mnt/disk1/jiayichen/code/MeshProcess/example_data/output/e9e567517b434ebd9890c52edfe4eed9/point_clouds/complete.npy"
pc = np.load(np_path).astype(np.float32)
tm_mesh.vertices = (tm_mesh.vertices - obb_transform[:3, 3][None]) @ obb_transform[
    :3, :3
]
# tm_mesh.vertices = (
#     tm_mesh.vertices @ obb_transform[:3, :3].transpose(-1, -2)
#     + obb_transform[:3, 3][None]
# )
print(tm_mesh.bounding_box_oriented.primitive.transform)
print(tm_mesh.bounding_box_oriented.primitive.extents)

new_pc = (pc - obb_transform[:3, 3][None]) @ obb_transform[:3, :3]
np.savetxt("debug.txt", new_pc)
import pdb

pdb.set_trace()
