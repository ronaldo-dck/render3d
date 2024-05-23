import numpy as np
import trimesh
import matplotlib.pyplot as plt

def close_polyline(polyline):
    # Adiciona o primeiro ponto novamente ao final da polyline
    closed_polyline = polyline + [polyline[0]]
    return closed_polyline

def generate_3d_object(points_2d, divisions):
    # Inicializa as listas de vértices e faces
    vertices = []
    faces = []
    
    # Gera os pontos 3D pela rotação ao redor do eixo X
    theta = np.linspace(0, 2 * np.pi, divisions, endpoint=False)
    for x, y in points_2d:
        for angle in theta:
            z = y * np.cos(angle)
            y_rot = y * np.sin(angle)
            vertices.append([x, y_rot, z])
    
    # Converte a lista de vértices em um array do numpy
    vertices = np.array(vertices)
    
    # Define as faces do objeto 3D
    num_points = len(points_2d)
    for i in range(num_points):
        for j in range(divisions):
            current = i * divisions + j
            next_ = i * divisions + (j + 1) % divisions
            if i < num_points - 1:
                current_top = current
                current_bottom = (i + 1) * divisions + j
                next_top = next_
                next_bottom = (i + 1) * divisions + (j + 1) % divisions
                
                faces.append([current_top, next_top, next_bottom])
                faces.append([current_top, next_bottom, current_bottom])
    
    # Converte a lista de faces em um array do numpy
    faces = np.array(faces)
    
    # Cria o objeto trimesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
   

# Definir os pontos 2D e o número de divisões
polyline = [(20, 40),(40, 40)]  # Exemplo de polyline
# polyline = close_polyline(polyline)  # Fecha a polyline para formar um polígono
divisions = 4  # Número de divisões para a rotação

# Gerar o objeto 3D
mesh = generate_3d_object(polyline, divisions)

# Visualizar o objeto 3D usando matplotlib
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Adiciona os vértices ao gráfico
ax.plot_trisurf(mesh.vertices[:,0], mesh.vertices[:,1], mesh.vertices[:,2], triangles=mesh.faces, cmap='viridis', edgecolor='none')

# Configurações do gráfico
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()
