import torch_harmonics
import trimesh
import torch
import numpy as np
import time

import torch_harmonics
import trimesh
import torch
import numpy as np


def cartesian_to_spherical(points):
    x, y, z = points[..., 0], points[..., 1], points[..., 2]
    r = torch.sqrt(x**2 + y**2 + z**2)
    theta = torch.acos(z / r)  # Polar angle
    phi = torch.atan2(y, x)  # Azimuthal angle
    return r, theta, phi


def spherical_grid_to_point_cloud(spherical_grid, nlat=64, nlon=128):
    batch_size = 1
    theta = torch.linspace(0, torch.pi, steps=nlat).view(1, nlat, 1)
    phi = torch.linspace(-torch.pi, torch.pi, steps=nlon).view(1, 1, nlon)

    theta = theta.expand(batch_size, nlat, nlon)
    phi = phi.expand(batch_size, nlat, nlon)
    r = spherical_grid

    # Convert to Cartesian coordinates
    x = r * torch.sin(theta) * torch.cos(phi)
    y = r * torch.sin(theta) * torch.sin(phi)
    z = r * torch.cos(theta)

    return torch.stack((x, y, z), dim=-1).view(batch_size, -1, 3)


path = "/mnt/disk1/jiayichen/code/cuDex/src/curobo/content/assets/object/new_meshdata/core_mug_546648204a20b712dfb0e477a80dcc95/mesh/simplified.obj"
tm = trimesh.load(path, force="mesh")
a = time.time()
ray_direction = spherical_grid_to_point_cloud(1.0)[0]
p, ind, _ = tm.ray.intersects_location(
    2 * ray_direction.numpy(), -ray_direction.numpy(), multiple_hits=False
)
inv_ind = [0] * 8192
for i in range(8192):
    inv_ind[ind[i]] = i
spherical_grid = torch.tensor(p[inv_ind]).norm(dim=-1).reshape(1, 64, 128)
print(time.time() - a)
# Transform to Spherical Harmonics domain and inverse back
sht = torch_harmonics.RealSHT(nlat=64, nlon=128, lmax=6, mmax=12, grid="equiangular")
feature = sht(spherical_grid)
inverse_sht = torch_harmonics.InverseRealSHT(
    nlat=64, nlon=128, lmax=6, mmax=12, grid="equiangular"
)
recon_grid = inverse_sht(feature)
print((recon_grid - spherical_grid).abs().max())

# Convert the inverse grid to point cloud
recon_pc = spherical_grid_to_point_cloud(recon_grid)
print(recon_pc.shape)
debug_pc = spherical_grid_to_point_cloud(spherical_grid)
print(time.time() - a)

np.savetxt("debug.txt", p)
np.savetxt("debug_pc.txt", debug_pc[0].numpy())
np.savetxt("reconstructed_pc.txt", recon_pc[0].numpy())
