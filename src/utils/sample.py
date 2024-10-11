import numpy as np
from .rotation import np_normalize


def even_sample_points_on_sphere(dim_num, delta_angle=45):
    """
    The method comes from https://stackoverflow.com/a/62754601
    Sample angles evenly in each dimension and finally normalize to sphere.
    """
    assert 90 % delta_angle == 0
    point_per_dim = 90 // delta_angle + 1
    point_num = point_per_dim ** (dim_num - 1) * dim_num * 2
    # print(f"Start to generate {point_num} points (with duplication) on S^{dim_num-1}!")

    comb = np.arange(point_per_dim ** (dim_num - 1))
    comb_lst = []
    for i in range(dim_num - 1):
        comb_lst.append(comb % point_per_dim)
        comb = comb // point_per_dim
    comb_array = np.stack(comb_lst, axis=-1)  # [p, d-1]

    # used to remove duplicated points!
    has_one = ((comb_array == point_per_dim - 1) | (comb_array == 0)) * np.arange(
        start=1, stop=dim_num
    )
    has_one = np.where(has_one == 0, dim_num, has_one)
    has_one = has_one.min(axis=-1)

    points_lst = []
    angle_array = (comb_array * delta_angle - 45) * np.pi / 180
    points_part = np.tan(angle_array)
    np_ones = np.ones_like(points_part[:, 0:1])  # [p, 1]
    for i in range(dim_num):
        pp1 = points_part[np.where(i < has_one)[0], :]  # remove duplicated points!
        points = np.concatenate(
            [
                np.concatenate([pp1[:, :i], np_ones[: pp1.shape[0]]], axis=-1),
                pp1[:, i:],
            ],
            axis=-1,
        )
        points_lst.append(points)

        pp2 = points_part[np.where(i < has_one)[0], :]  # remove duplicated points!
        points2 = np.concatenate(
            [
                np.concatenate([pp2[:, :i], -np_ones[: pp2.shape[0]]], axis=-1),
                pp2[:, i:],
            ],
            axis=-1,
        )
        points_lst.append(points2)

    points_array = np.concatenate(points_lst, axis=0)  # [P, d]
    points_array = np_normalize(points_array)
    # print(f"Finish generating! Got {points_array.shape[0]} points (without duplication) on S^{dim_num-1}!")
    return points_array


if __name__ == "__main__":
    rr = even_sample_points_on_sphere(4, delta_angle=45)
    print(rr)
