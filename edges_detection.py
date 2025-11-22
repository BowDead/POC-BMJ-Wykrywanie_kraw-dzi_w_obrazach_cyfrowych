import cv2
import numpy as np
from edges_methods import sobel_edges, laplacian_edges, scharr_edges, prewitt_edges, canny_edges, roberts_edges

def detect_edges(img, color_space='RGB', method='Sobel',
                 translations_getter=None, low_threshold=0, high_threshold=255):

    if translations_getter is None:
        def get_text(key): return key
    else:
        get_text = translations_getter

    if img is None:
        raise ValueError(get_text("INVALID_IMAGE"))

    methods_dict = {
        'Sobel': sobel_edges,
        'Laplacian': laplacian_edges,
        'Scharr': scharr_edges,
        'Prewitt': prewitt_edges,
        'Canny': canny_edges,
        'Roberts': roberts_edges
    }

    if method not in methods_dict:
        raise ValueError(get_text("UNKNOWN_METHOD"))

    edge_func = methods_dict[method]
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # --------------------------------------------------
    #  RGB
    # --------------------------------------------------
    if color_space == 'RGB':
        R, G, B = cv2.split(img_rgb)
        edges_R = edge_func(R, low_threshold, high_threshold)
        edges_G = edge_func(G, low_threshold, high_threshold)
        edges_B = edge_func(B, low_threshold, high_threshold)

        edges = [edges_R, edges_G, edges_B]
        if method == 'Canny':
            edges_sum = np.maximum.reduce(edges)
        else:
            edges_sum = cv2.addWeighted(
                cv2.addWeighted(edges_R, 1/3, edges_G, 1/3, 0),
                1, edges_B, 1/3, 0
            )

        titles = [
            get_text('CHANNEL_R'),
            get_text('CHANNEL_G'),
            get_text('CHANNEL_B'),
            get_text('EDGE_SUM_TITLE')
        ]

    # --------------------------------------------------
    #  HSV
    # --------------------------------------------------
    elif color_space == 'HSV':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        H, S, V = cv2.split(hsv)

        edges_H = edge_func(H, low_threshold, high_threshold)
        edges_S = edge_func(S, low_threshold, high_threshold)
        edges_V = edge_func(V, low_threshold, high_threshold)

        edges = [edges_H, edges_S, edges_V]
        if method == 'Canny':
            edges_sum = np.maximum.reduce(edges)
        else:
            edges_sum = np.maximum(np.maximum(edges_H, edges_S), edges_V)

        titles = [
            get_text('CHANNEL_H'),
            get_text('CHANNEL_S'),
            get_text('CHANNEL_V'),
            get_text('EDGE_SUM_TITLE')
        ]

    # --------------------------------------------------
    #  LAB
    # --------------------------------------------------
    elif color_space == 'LAB':
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(lab)

        edges_L = edge_func(L, low_threshold, high_threshold)
        edges_A = edge_func(A, low_threshold, high_threshold)
        edges_B = edge_func(B, low_threshold, high_threshold)

        edges = [edges_L, edges_A, edges_B]

        # suma wektorowa
        if method == 'Canny':
            edges_sum = np.maximum.reduce(edges)
        else:
            edges_sum = np.sqrt(
                edges_L.astype(np.float64)**2 +
                edges_A.astype(np.float64)**2 +
                edges_B.astype(np.float64)**2
            )
            edges_sum = cv2.normalize(edges_sum, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        titles = [
            get_text('CHANNEL_L'),
            get_text('CHANNEL_A'),
            get_text('CHANNEL_B'),
            get_text('EDGE_SUM_TITLE')
        ]

    # --------------------------------------------------
    #  CMYK
    # --------------------------------------------------
    elif color_space == 'CMYK':
        rgb = img_rgb.astype(np.float32) / 255.0
        r, g, b = cv2.split(rgb)

        c = 1 - r
        m = 1 - g
        y = 1 - b

        k = np.minimum(np.minimum(c, m), y)

        denom = 1 - k
        denom[denom == 0] = 1

        c_final = (c - k) / denom
        m_final = (m - k) / denom
        y_final = (y - k) / denom

        C = (c_final * 255).astype(np.uint8)
        M = (m_final * 255).astype(np.uint8)
        Y = (y_final * 255).astype(np.uint8)
        K = (k * 255).astype(np.uint8)

        edges_C = edge_func(C, low_threshold, high_threshold)
        edges_M = edge_func(M, low_threshold, high_threshold)
        edges_Y = edge_func(Y, low_threshold, high_threshold)
        edges_K = edge_func(K, low_threshold, high_threshold)

        edges = [edges_C, edges_M, edges_Y, edges_K]

        if method == 'Canny':
            edges_sum = np.maximum.reduce(edges)
        else:
            edges_sum = np.max(np.stack(edges, axis=0), axis=0)
        titles = [
            get_text('CHANNEL_C'),
            get_text('CHANNEL_M'),
            get_text('CHANNEL_Y'),
            get_text('CHANNEL_K'),
            get_text('EDGE_SUM_TITLE')
        ]

    else:
        raise ValueError(get_text("UNKNOWN_COLOR_SPACE"))

    return img_rgb, edges, edges_sum, titles