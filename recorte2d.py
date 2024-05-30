import matplotlib.patches as patches
import matplotlib.pyplot as plt


def inside(point, edge, x_min, y_min, x_max, y_max):
    if edge == "left":
        return point[0] > x_min
    elif edge == "right":
        return point[0] < x_max
    elif edge == "bottom":
        return point[1] > y_min
    elif edge == "top":
        return point[1] < y_max


def intersection(point1, point2, color1, color2, edge, x_min, y_min, x_max, y_max):
    if edge == "left":
        x = x_min
        factor = (x_min - point1[0]) / (point2[0] - point1[0]) if (point2[0] - point1[0]) != 0 else 0
    elif edge == "right":
        x = x_max
        factor = (x_max - point1[0]) / (point2[0] - point1[0]) if (point2[0] - point1[0]) != 0 else 0
    elif edge == "bottom":
        y = y_min
        factor = (y_min - point1[1]) / (point2[1] - point1[1]) if (point2[1] - point1[1]) != 0 else 0
        x = point1[0] + (point2[0] - point1[0]) * factor
    elif edge == "top":
        y = y_max
        factor = (y_max - point1[1]) / (point2[1] - point1[1]) if (point2[1] - point1[1]) != 0 else 0
        x = point1[0] + (point2[0] - point1[0]) * factor

    if edge in ["left", "right"]:
        y = point1[1] + (point2[1] - point1[1]) * factor
    z = point1[2] + (point2[2] - point1[2]) * factor
    color = [color1[i] + (color2[i] - color1[i]) * factor for i in range(3)]

    return (x, y, z), color


def sutherland_hodgman_clip(polygon, polygon_colors, x_min, y_min, x_max, y_max):
    def clip_polygon(polygon, polygon_colors, edge):
        clipped_polygon = []
        clipped_polygon_colors = []
        for i in range(len(polygon)):
            current_point = polygon[i]
            current_color = polygon_colors[i]
            prev_point = polygon[i - 1]
            prev_color = polygon_colors[i - 1]
            if inside(current_point, edge, x_min, y_min, x_max, y_max):
                if not inside(prev_point, edge, x_min, y_min, x_max, y_max):
                    p, color = intersection(prev_point, current_point, prev_color, current_color, edge, x_min, y_min, x_max, y_max)
                    clipped_polygon.append(p)
                    clipped_polygon_colors.append(color)
                clipped_polygon.append(current_point)
                clipped_polygon_colors.append(current_color)
            elif inside(prev_point, edge, x_min, y_min, x_max, y_max):
                p, color = intersection(prev_point, current_point, prev_color, current_color, edge, x_min, y_min, x_max, y_max)
                clipped_polygon.append(p)
                clipped_polygon_colors.append(color)
        return clipped_polygon, clipped_polygon_colors

    edges = ["left", "right", "bottom", "top"]
    for edge in edges:
        polygon, polygon_colors = clip_polygon(polygon, polygon_colors, edge)
    return polygon, polygon_colors


def triangulate_convex_polygon(polygon, polygon_colors):
    if len(polygon) < 3:
        raise ValueError("O polígono deve ter pelo menos 3 vértices")

    reference_point = polygon[0]
    reference_color = polygon_colors[0]
    triangles = []
    triangles_colors = []
    for i in range(1, len(polygon) - 1):
        triangle = (reference_point, polygon[i], polygon[i + 1])
        triangle_colors = (reference_color, polygon_colors[i], polygon_colors[i + 1])
        triangles.append(triangle)
        triangles_colors.append(triangle_colors)
    return triangles, triangles_colors


def plot_polygons(original_polygon, original_colors, clipped_polygon, clipped_colors, triangles, x_min, y_min, x_max, y_max):
    fig, ax = plt.subplots()

    # Plot original polygon
    original_polygon.append(original_polygon[0])
    original_colors.append(original_colors[0])
    for i in range(len(original_polygon) - 1):
        x_original, y_original, _ = zip(*original_polygon[i:i+2])
        ax.plot(x_original, y_original, color=original_colors[i])

    # Plot clipped polygon
    if clipped_polygon:
        clipped_polygon.append(clipped_polygon[0])
        clipped_colors.append(clipped_colors[0])
        for i in range(len(clipped_polygon) - 1):
            x_clipped, y_clipped, _ = zip(*clipped_polygon[i:i+2])
            ax.plot(x_clipped, y_clipped, color=clipped_colors[i])

    # Plot triangles
    for triangle in triangles:
        x_tri, y_tri, _ = zip(*triangle)
        ax.plot(list(x_tri) + [x_tri[0]], list(y_tri) + [y_tri[0]], 'g--')

    # Plot clipping window
    rect = patches.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, linewidth=1, edgecolor='g', facecolor='none')
    ax.add_patch(rect)

    ax.set_title('Polygon Clipping and Triangulation')
    ax.set_xlim(min(x_min, min([p[0] for p in original_polygon])), max(x_max, max([p[0] for p in original_polygon])))
    ax.set_ylim(min(y_min, min([p[1] for p in original_polygon])), max(y_max, max([p[1] for p in original_polygon])))
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()


if __name__ == "__main__":
    polygon = [(151.914, 340.497, 0), (369.403, 223.801, 50), (149.556, -51.107, 100)]
    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]  # RGB colors for the vertices
    x_min, y_min = 0, 0
    x_max, y_max = 319, 239

    clipped_polygon, clipped_colors = sutherland_hodgman_clip(polygon, colors, x_min, y_min, x_max, y_max)
    triangles = triangulate_convex_polygon(clipped_polygon)
    plot_polygons(polygon, colors, clipped_polygon, clipped_colors, triangles, x_min, y_min, x_max, y_max)
    print("Polígono recortado:", clipped_polygon)
    print("Triângulos resultantes da triangulação:")
    for triangle in triangles:
        print(triangle)
