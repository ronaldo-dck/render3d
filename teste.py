


import numpy as np
import trimesh

def rotate_point(point, angle, axis='x'):
    """ Rotaciona um ponto em torno de um eixo por um determinado ângulo. """
    angle_rad = np.radians(angle)
    if axis == 'x':
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, np.cos(angle_rad), -np.sin(angle_rad)],
            [0, np.sin(angle_rad), np.cos(angle_rad)]
        ])
    else:
        raise ValueError("Apenas rotação no eixo x é suportada por enquanto.")
    
    return np.dot(rotation_matrix, point)


    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, edges=edges)
    return mesh

# Definindo a polilinha


# Definindo a polilinha
polyline = [
    [1, 2, 0],
    [2, 2, 0],
]


# Cria o modelo 3D
mesh = revolve_polyline(polyline)

# Salva o modelo em um arquivo
mesh.export('modelo_3d.obj')

# Exibir os vértices, faces e arestas
print("Vértices:\n", mesh.vertices)
print("Faces:\n", mesh.faces)
print("Arestas:\n", mesh.edges)
