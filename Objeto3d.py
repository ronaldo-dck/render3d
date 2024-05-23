import numpy as np
import numpy as np
import trimesh
import matplotlib.pyplot as plt

class Objeto3d:

    def __init__(self, polyline: list) -> None:
        self.__polyline: list = polyline
        self.__vertices = list()
        self.__faces = list()

    def rotacaoX(self, divisions: int) -> None:
        if len(self.__polyline) < 2:
            print("Erro: Insuficientes pontos para rotação.")
            return

        # Inicializa as listas de vértices e faces
        vertices = []
        faces = []
        arestas = []

        # Gera os pontos 3D pela rotação ao redor do eixo X
        theta = np.linspace(0, 2 * np.pi, divisions, endpoint=False)
        for x, y in self.__polyline:
            for angle in theta:
                y_rot = round(y * np.cos(angle), 2)
                z = round(y * np.sin(angle), 2)
                vertices.append([x, y_rot, z])

        # Converte a lista de vértices em um array do numpy
        vertices = np.array(vertices)

        # Define as faces do objeto 3D
        num_points = len(self.__polyline)
        for i in range(num_points - 1):
            for j in range(divisions):
                current = i * divisions + j
                next_ = i * divisions + (j + 1) % divisions

                current_top = current
                current_bottom = (i + 1) * divisions + j
                next_top = next_
                next_bottom = (i + 1) * divisions + (j + 1) % divisions

                # Adiciona as faces
                faces.append([current_top, next_top, next_bottom])
                faces.append([current_top, next_bottom, current_bottom])

                # Adiciona as arestas se ainda não foram adicionadas
        
        # Adiciona as arestas
        for i in range(num_points):
            for j in range(divisions):
                # Índice do vértice atual
                current = i * divisions + j
                
                # Índice do próximo vértice na mesma linha
                next_in_row = i * divisions + (j + 1) % divisions
                
                # Índice do próximo vértice na próxima linha
                next_row = (i + 1) * divisions + j
                
                # Adiciona a aresta entre o vértice atual e o próximo vértice na mesma linha
                arestas.append((current, next_in_row))
                
                # Adiciona a aresta entre o vértice atual e o próximo vértice na próxima linha, exceto na última linha
                if i < num_points - 1:
                    arestas.append((current, next_row))


        # Converte a lista de faces em um array do numpy
        faces = np.array(faces)
        # print(vertices)
        # print(arestas)
        # print(faces)

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
   

        self.__vertices = vertices
        self.__faces = faces
        self.__arestas = arestas
        return mesh

    def get_faces(self):
        return self.__faces

    def get_edges(self):
        return self.__arestas

    def get_vertices(self):
        return self.__vertices


if __name__ == '__main__':
    obj1 = Objeto3d([(2, 4),(4, 4)])
    
    # Gerar o objeto 3D
    mesh = obj1.rotacaoX(4)
    print(obj1.get_edges())
    # print(mesh)

    # Visualizar o objeto 3D usando matplotlib
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Adiciona os vértices ao gráfico
    ax.plot_trisurf(mesh.vertices[:,0], mesh.vertices[:,1], mesh.vertices[:,2], triangles=mesh.faces, cmap='viridis', edgecolor='none')
    # Adiciona os vértices ao gráfico

    # Configurações do gráfico
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()
