import numpy as np


def np_normalize(x_vec):
    return x_vec / np.maximum(np.linalg.norm(x_vec, axis=-1, keepdims=True), 1e-8)


def standardize_quaternion(quaternions):
    """
    Convert a unit quaternion to a standard form: one in which the real
    part is non negative.

    Args:
        quaternions: Quaternions with real part first,
            as tensor of shape (..., 4).

    Returns:
        Standardized quaternions as tensor of shape (..., 4).
    """
    return np.where(quaternions[..., 0:1] < 0, -quaternions, quaternions)


def batched_quat_inv(quaternions):
    """
    Computes the inverse of a batch of quaternions.

    Parameters:
    quaternions (np.ndarray): A batch of quaternions of shape (..., 4) where each quaternion is [w, x, y, z].

    Returns:
    np.ndarray: The inverses of the input quaternions of shape (..., 4).
    """
    inverses = np.copy(quaternions)
    inverses[..., 1:] = -inverses[..., 1:]
    return inverses


def batched_quat_multiply(quaternion0, quaternion1):
    """
    Computes the multiply of two batches of quaternions.

    Parameters:
    quaternion0 (np.ndarray): A batch of quaternions of shape (..., 4) where each quaternion is [w, x, y, z].
    quaternion1 (np.ndarray): A batch of quaternions of shape (..., 4) where each quaternion is [w, x, y, z].

    Returns:
    np.ndarray: The mutiplied result of the input quaternions of shape (..., 4).
    """
    w0, x0, y0, z0 = np.split(quaternion0, 4, axis=-1)
    w1, x1, y1, z1 = np.split(quaternion1, 4, axis=-1)
    return standardize_quaternion(
        np.concatenate(
            (
                -x1 * x0 - y1 * y0 - z1 * z0 + w1 * w0,
                x1 * w0 + y1 * z0 - z1 * y0 + w1 * x0,
                -x1 * z0 + y1 * w0 + z1 * x0 + w1 * y0,
                x1 * y0 - y1 * x0 + z1 * w0 + w1 * z0,
            ),
            axis=-1,
        )
    )


def batched_quat_to_axisangle(quaternions):
    """
    Converts a batch of quaternions to axis-angle representation.

    Parameters:
    quaternions (np.ndarray): A batch of quaternions of shape (..., 4) where each quaternion is [w, x, y, z].

    Returns:
    Tuple:
        - angles (np.ndarray): A batch of rotation angles in radians of shape (...,).
        - axes (np.ndarray): A batch of rotation axes of shape (..., 3).
    """
    # Extract the scalar part (w) and vector part (x, y, z)
    w = quaternions[..., 0]
    vec = quaternions[..., 1:]

    # Compute the rotation angle: angle = 2 * arccos(w)
    angles = 2 * np.arccos(
        np.clip(w, -1.0, 1.0)
    )  # Clip to avoid numerical issues with arccos

    # Compute the rotation axis by normalizing the vector part (x, y, z)
    norm_vec = np.linalg.norm(vec, axis=-1, keepdims=True)
    axes = np.divide(
        vec, norm_vec, out=np.zeros_like(vec), where=(norm_vec != 0)
    )  # Handle zero division

    return angles, axes


def batched_quat_delta(q0, q1):
    return batched_quat_to_axisangle(batched_quat_multiply(batched_quat_inv(q0), q1))


def batched_quat_to_mat(q):
    """Convert rotations given as quaternions to rotation matrices.

    Args:
        quaternions (np.ndarray): A batch of quaternions of shape (..., 4) where each quaternion is [w, x, y, z].

    Returns:
        Rotation matrices as array of shape (..., 3, 3).
    """

    r, i, j, k = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    two_s = 2.0 / np.sum(q * q, axis=-1)

    o = np.stack(
        (
            1 - two_s * (j * j + k * k),
            two_s * (i * j - k * r),
            two_s * (i * k + j * r),
            two_s * (i * j + k * r),
            1 - two_s * (i * i + k * k),
            two_s * (j * k - i * r),
            two_s * (i * k - j * r),
            two_s * (j * k + i * r),
            1 - two_s * (i * i + j * j),
        ),
        axis=-1,
    )

    return o.reshape(*q.shape[:-1], 3, 3)


if __name__ == "__main__":
    q1 = np_normalize(np.array([0.07210599, 0.20452067, 0.12467231, 0.96820909]))
    q2 = np_normalize(np.array([0.97031647, 0.13278606, 0.19933981, 0.03342843]))
    delta_quat = batched_quat_multiply(batched_quat_inv(q1), q2)
    angle, axis = batched_quat_to_axisangle(delta_quat)
    print(np.degrees(angle), axis)
