import numpy as np

def triangulation(quads: np.array) -> np.array:
    """
    Convert a quadrilateral mesh into a triangle mesh.

    :quads: List of quadrilateral cells, where each cell is a list of four vertex indices.
    :return: List of triangle cells with their original face_id, where each cell is a list of three vertex indices.
    """
    triangles = np.zeros((len(quads) *2, 3), dtype=np.int32)

    # iteration variables
    face_idx = 0
    increment = 2

    for quad in quads:
        # Extract vertex indices from the quadrilateral cell
        v0, v1, v2, v3 = quad

        # Create two triangles using the quadrilateral vertices and the new vertex
        triangles[face_idx]=[v0, v1, v2]
        triangles[face_idx + 1] = [v2, v3, v0]
        face_idx += increment 

    return triangles

def mieses_stress(stress_tensor: np.array) -> np.array:
    """
    Calculate the stress tensor for a given set of stress components.
    
    :stress_tensor: A list of stress components in the format [sigma_xx, sigma_yy, sigma_zz, sigma_xy, sigma_yz, sigma_zx].
    :return: The mieses stress tensor as a 3x3 array.
    """
    sigma_xx, sigma_yy, sigma_zz, sigma_xy, sigma_yz, sigma_zx = stress_tensor
    return np.sqrt(((sigma_xx - sigma_yy)**2 + (sigma_yy - sigma_zz)**2 + (sigma_zz - sigma_xx)**2 + 6*(sigma_xy**2 + sigma_yz**2 + sigma_zx**2)) / 2)