import matplotlib.pyplot as plt
import matplotlib.patches as patches

def inside(point, edge, x_min, y_min, x_max, y_max):
    if edge == "left":
        return point[0] > x_min
    elif edge == "right":
        return point[0] < x_max
    elif edge == "bottom":
        return point[1] > y_min
    elif edge == "top":
        return point[1] < y_max

def intersection(point1, point2, edge, x_min, y_min, x_max, y_max):
    if edge == "left":
        x = x_min
        y = point1[1] + (point2[1] - point1[1]) * (x_min - point1[0]) / (point2[0] - point1[0])
        z = point1[2] + (point2[2] - point1[2]) * (x_min - point1[0]) / (point2[0] - point1[0])
    elif edge == "right":
        x = x_max
        y = point1[1] + (point2[1] - point1[1]) * (x_max - point1[0]) / (point2[0] - point1[0])
        z = point1[2] + (point2[2] - point1[2]) * (x_max - point1[0]) / (point2[0] - point1[0])
    elif edge == "bottom":
        y = y_min
        x = point1[0] + (point2[0] - point1[0]) * (y_min - point1[1]) / (point2[1] - point1[1])
        z = point1[2] + (point2[2] - point1[2]) * (y_min - point1[1]) / (point2[1] - point1[1])
    elif edge == "top":
        y = y_max
        x = point1[0] + (point2[0] - point1[0]) * (y_max - point1[1]) / (point2[1] - point1[1])
        z = point1[2] + (point2[2] - point1[2]) * (y_max - point1[1]) / (point2[1] - point1[1])
    return (x, y, z)

def sutherland_hodgman_clip(polygon, x_min, y_min, x_max, y_max):
    def clip_polygon(polygon, edge):
        clipped_polygon = []
        for i in range(len(polygon)):
            current_point = polygon[i]
            prev_point = polygon[i - 1]
            if inside(current_point, edge, x_min, y_min, x_max, y_max):
                if not inside(prev_point, edge, x_min, y_min, x_max, y_max):
                    clipped_polygon.append(intersection(prev_point, current_point, edge, x_min, y_min, x_max, y_max))
                clipped_polygon.append(current_point)
            elif inside(prev_point, edge, x_min, y_min, x_max, y_max):
                clipped_polygon.append(intersection(prev_point, current_point, edge, x_min, y_min, x_max, y_max))
        return clipped_polygon

    edges = ["left", "right", "bottom", "top"]
    for edge in edges:
        polygon = clip_polygon(polygon, edge)
    return polygon

def triangulate_convex_polygon(polygon):
    """
    Dado um polígono convexo, retorna uma lista de triângulos que compõem o polígono.
    
    Args:
    polygon (list of tuples): Lista de vértices do polígono. Cada vértice é uma tupla (x, y, z).
    
    Returns:
    list of tuples: Lista de triângulos. Cada triângulo é representado por uma tupla contendo três vértices.
    """
    if len(polygon) < 3:
        raise ValueError("O polígono deve ter pelo menos 3 vértices")

    # Escolher o primeiro vértice como ponto de referência
    reference_point = polygon[0]
    
    # Lista para armazenar os triângulos
    triangles = []

    # Criar triângulos usando o vértice de referência e pares consecutivos de outros vértices
    for i in range(1, len(polygon) - 1):
        triangle = (reference_point, polygon[i], polygon[i + 1])
        triangles.append(triangle)
    
    return triangles

def plot_polygons(original_polygon, clipped_polygon, triangles, x_min, y_min, x_max, y_max):
    fig, ax = plt.subplots()

    # Plot original polygon
    original_polygon.append(original_polygon[0])  # Ensure the polygon is closed
    x_original, y_original, _ = zip(*original_polygon)
    ax.plot(x_original, y_original, 'b-', label='Original Polygon')

    # Plot clipped polygon
    if clipped_polygon:
        clipped_polygon.append(clipped_polygon[0])  # Ensure the polygon is closed
        x_clipped, y_clipped, _ = zip(*clipped_polygon)
        ax.plot(x_clipped, y_clipped, 'r-', label='Clipped Polygon')

    # Plot triangles
    for triangle in triangles:
        x_tri, y_tri, _ = zip(*triangle)
        ax.plot(list(x_tri) + [x_tri[0]], list(y_tri) + [y_tri[0]], 'g--', label='Triangle')

    # Plot clipping window
    rect = patches.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, linewidth=1, edgecolor='g', facecolor='none', label='Clipping Window')
    ax.add_patch(rect)

    # Add labels and
    # Add labels and legend
    ax.set_title('Polygon Clipping and Triangulation')
    ax.legend()
    ax.set_xlim(min(x_min, min(x_original)), max(x_max, max(x_original)))
    ax.set_ylim(min(y_min, min(y_original)), max(y_max, max(y_original)))
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()

if __name__ == "__main__":
    polygon = [(151.914, 340.497, 0), (369.403, 223.801, 50), (149.556, -51.107, 100)]
    x_min, y_min = 0, 0
    x_max, y_max = 319, 239

    clipped_polygon = sutherland_hodgman_clip(polygon, x_min, y_min, x_max, y_max)
    triangles = triangulate_convex_polygon(clipped_polygon)
    plot_polygons(polygon, clipped_polygon, triangles, x_min, y_min, x_max, y_max)
    print("Polígono recortado:", clipped_polygon)
    print("Triângulos resultantes da triangulação:")
    for triangle in triangles:
        print(triangle)
