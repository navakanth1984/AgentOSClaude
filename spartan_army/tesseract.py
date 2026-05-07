import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import itertools

def generate_tesseract_edges():
    # 16 vertices of a 4D hypercube
    vertices = list(itertools.product([-1, 1], repeat=4))
    edges = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            # Edges exist between vertices that differ by exactly one coordinate
            diff = np.array(vertices[i]) - np.array(vertices[j])
            if np.count_nonzero(diff) == 1:
                edges.append((vertices[i], vertices[j]))
    return edges

def project_4d_to_3d(point, distance=2):
    x, y, z, w = point
    # Perspective projection from 4D to 3D
    factor = distance / (distance - w)
    return [x * factor, y * factor, z * factor]

def render_tesseract(output_path):
    edges = generate_tesseract_edges()
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Project and plot edges
    for start, end in edges:
        p1 = project_4d_to_3d(start)
        p2 = project_4d_to_3d(end)
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='blue', alpha=0.6)

    # Project and plot vertices
    vertices = list(itertools.product([-1, 1], repeat=4))
    for v in vertices:
        p = project_4d_to_3d(v)
        ax.scatter(p[0], p[1], p[2], color='red', s=20)

    ax.set_title("4D Tesseract Projection (3D Perspective)")
    ax.set_axis_off()
    
    plt.savefig(output_path, format='jpg', dpi=150)
    print(f"Successfully saved 4D model to {output_path}")

if __name__ == "__main__":
    try:
        render_tesseract("spartan_army/Tesseract_Visualization.jpg")
    except Exception as e:
        print(f"Error rendering model: {e}")
