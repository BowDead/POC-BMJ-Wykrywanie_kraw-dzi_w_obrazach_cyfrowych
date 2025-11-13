import cv2
import numpy as np
from edges_methods import sobel_edges, laplacian_edges, scharr_edges

def detect_edges(img, color_space='RGB', method='Sobel'):
    """
    Wykrywa krawędzie w wybranym systemie kolorów i metodą detekcji.
    Zwraca: img_rgb, lista krawędzi kanałów, suma krawędzi, tytuły kanałów
    """
    if img is None:
        raise ValueError("Nieprawidłowy obraz (None).")

    methods_dict = {'Sobel': sobel_edges, 'Laplacian': laplacian_edges, 'Scharr': scharr_edges}
    if method not in methods_dict:
        raise ValueError("Nieznana metoda wykrywania krawędzi.")
    edge_func = methods_dict[method]

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if color_space == 'RGB':
        channels = cv2.split(img_rgb)
        edges = [edge_func(c) for c in channels]
        edges_sum = cv2.addWeighted(cv2.addWeighted(edges[0], 1/3, edges[1], 1/3, 0), 1, edges[2], 1/3, 0)
        titles = ['R', 'G', 'B', 'Suma krawędzi']

    elif color_space == 'HSV':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        edges = [edge_func(h), edge_func(s), edge_func(v)]
        edges_sum = cv2.max(edges[0], cv2.max(edges[1], edges[2]))
        titles = ['H', 'S', 'V', 'Suma krawędzi']

    elif color_space == 'LAB':
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Wyliczamy krawędzie
        edges_l = edge_func(l)
        edges_a = edge_func(a)
        edges_b = edge_func(b)
        
        # Wektorowa suma gradientów
        edges_sum = np.sqrt(edges_l.astype(np.float64)**2 + 
                            edges_a.astype(np.float64)**2 + 
                            edges_b.astype(np.float64)**2)
        
        # Normalizacja do 0-255
        edges_sum = cv2.normalize(edges_sum, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        edges_l = cv2.normalize(edges_l, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        edges_a = cv2.normalize(edges_a, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        edges_b = cv2.normalize(edges_b, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        edges = [edges_l, edges_a, edges_b]
        titles = ['L', 'A', 'B', 'Suma krawędzi']

    else:
        raise ValueError("Nieznany system kolorów.")

    return img_rgb, edges, edges_sum, titles
