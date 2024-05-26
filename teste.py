import numpy as np
import matplotlib.pyplot as plt

def z_buffer(vertices):
    # Encontre os limites do polígono
    min_x = min(vertices, key=lambda vertex: vertex[0])[0]
    max_x = max(vertices, key=lambda vertex: vertex[0])[0]
    min_y = min(vertices, key=lambda vertex: vertex[1])[1]
    max_y = max(vertices, key=lambda vertex: vertex[1])[1]
    
    # Inicialize o Z-buffer
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    z_buffer = np.full((height, width), float('inf'))
    
    # Para cada linha de varredura
    for y in range(min_y, max_y + 1):
        intersections = []
        # Inicialize os valores de x_prev e z_prev
        x_prev = None
        z_prev = None
        # Para cada aresta do polígono
        for i in range(len(vertices)):
            j = (i + 1) % len(vertices)
            # Verifique se a aresta cruza a linha de varredura atual
            if (vertices[i][1] <= y <= vertices[j][1]) or (vertices[j][1] <= y <= vertices[i][1]):
                # Calcule a interseção da aresta com a linha de varredura
                if vertices[i][1] != vertices[j][1]:
                    x_intersect = vertices[i][0] + (y - vertices[i][1]) * (vertices[j][0] - vertices[i][0]) / (vertices[j][1] - vertices[i][1])
                    z_intersect = vertices[i][2] + (y - vertices[i][1]) * (vertices[j][2] - vertices[i][2]) / (vertices[j][1] - vertices[i][1])
                else:
                    # Se a aresta é horizontal, use o valor do vértice inferior
                    x_intersect = vertices[i][0]
                    z_intersect = vertices[i][2]
                
                # Adicione a interseção à lista de interseções
                intersections.append((x_intersect, z_intersect))
        
        # Classifique as interseções com base em x
        intersections.sort(key=lambda intersection: intersection[0])
        
        # Preencha os pixels entre as interseções
        for i in range(0, len(intersections), 2):
            x_start = max(min_x, int(intersections[i][0]))
            x_end = min(max_x, int(intersections[i + 1][0]))
            for x in range(x_start, x_end + 1):
                z_buffer[y - min_y, x - min_x] = min(intersections[i][1], z_buffer[y - min_y, x - min_x])

    return z_buffer

def plot_z_buffer(z_buffer):
    plt.imshow(z_buffer, cmap='viridis', origin='lower')
    plt.colorbar(label='Profundidade')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title('Z-buffer')
    plt.show()

# Exemplo de uso
vertices = [(0, 0, 0), (2, 4, 1), (5, 2, 2)]
z_buffer_result = z_buffer(vertices)
plot_z_buffer(z_buffer_result)
