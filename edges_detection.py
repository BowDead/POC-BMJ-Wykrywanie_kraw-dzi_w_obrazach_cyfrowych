import cv2
import numpy as np
from edges_methods import sobel_edges, laplacian_edges, scharr_edges, prewitt_edges

# Zmieniona sygnatura funkcji (dodajemy translations_getter)
def detect_edges(img, color_space='RGB', method='Sobel', translations_getter=None):
    """
    Wykrywa krawędzie w wybranym systemie kolorów i metodą detekcji.
    Zwraca: img_rgb, lista krawędzi kanałów, suma krawędzi, tytuły kanałów
    """

    # Utwórz lokalną funkcję get_text, jeśli została przekazana
    if translations_getter is None:
        # Fallback: jeśli funkcja tłumacząca nie została przekazana, zwracamy klucz
        def get_text(key): return key
    else:
        get_text = translations_getter

    if img is None:
        raise ValueError(get_text("INVALID_IMAGE")) # Tłumaczenie błędu

    methods_dict = {'Sobel': sobel_edges, 'Laplacian': laplacian_edges, 'Scharr': scharr_edges, 'Prewitt': prewitt_edges}
    if method not in methods_dict:
        raise ValueError(get_text("UNKNOWN_METHOD")) # Tłumaczenie błędu
    edge_func = methods_dict[method]

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if color_space == 'RGB':
        channels = cv2.split(img_rgb)
        edges = [edge_func(c) for c in channels]
        edges_sum = cv2.addWeighted(cv2.addWeighted(edges[0], 1/3, edges[1], 1/3, 0), 1, edges[2], 1/3, 0)
        # Użycie get_text dla tytułów
        titles = [get_text('CHANNEL_R'), get_text('CHANNEL_G'), get_text('CHANNEL_B'), get_text('EDGE_SUM_TITLE')]

    elif color_space == 'HSV':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        edges = [edge_func(h), edge_func(s), edge_func(v)]
        edges_sum = cv2.max(edges[0], cv2.max(edges[1], edges[2]))
        # Użycie get_text dla tytułów
        titles = [get_text('CHANNEL_H'), get_text('CHANNEL_S'), get_text('CHANNEL_V'), get_text('EDGE_SUM_TITLE')]

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
        # Użycie get_text dla tytułów
        titles = [get_text('CHANNEL_L'), get_text('CHANNEL_A'), get_text('CHANNEL_B'), get_text('EDGE_SUM_TITLE')]

    elif color_space == 'CMYK':
        # Konwersja RGB -> CMYK (własnoręczna, bez PIL)
        rgb = img_rgb.astype(np.float32) / 255.0
        r, g, b = cv2.split(rgb)

        # Obliczenie kanałów CMY
        c = 1 - r
        m = 1 - g
        y = 1 - b

        # Kanał K = minimum z CMY
        k = np.minimum(np.minimum(c, m), y)

        # Unikamy dzielenia przez zero
        denom = 1 - k
        denom[denom == 0] = 1

        # Obliczenie właściwych C, M, Y (drukarskich)
        c_final = (c - k) / denom
        m_final = (m - k) / denom
        y_final = (y - k) / denom

        # Normalizacja 0–255 uint8
        C = (c_final * 255).astype(np.uint8)
        M = (m_final * 255).astype(np.uint8)
        Y = (y_final * 255).astype(np.uint8)
        K = (k * 255).astype(np.uint8)

        # Wykrywanie krawędzi
        edges_C = edge_func(C)
        edges_M = edge_func(M)
        edges_Y = edge_func(Y)
        edges_K = edge_func(K)

        edges = [edges_C, edges_M, edges_Y, edges_K]

        # Suma: maksymalna odpowiedź z kanałów
        edges_sum = np.max(np.stack(edges, axis=0), axis=0)

        # Użycie get_text dla tytułów
        titles = [get_text('CHANNEL_C'), get_text('CHANNEL_M'), get_text('CHANNEL_Y'), get_text('CHANNEL_K'), get_text('EDGE_SUM_TITLE')]

    else:
        raise ValueError(get_text("UNKNOWN_COLOR_SPACE")) # Tłumaczenie błędu

    return img_rgb, edges, edges_sum, titles