import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_edges_lab(img):
    """
    Wykrywanie krawędzi w przestrzeni LAB z wykorzystaniem operatora Sobela.
    Argument:
        img: obraz wczytany przez cv2.imread() (BGR)
    """
    # Sprawdzenie poprawności
    if img is None:
        raise ValueError("Nieprawidłowy obraz (None).")

    # Konwersje
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    # Rozdzielenie kanałów
    l, a, b = cv2.split(img_lab)

    # Funkcja Sobel (bez normalizacji)
    def sobel_edges(channel):
        ch = channel.astype(np.float64)
        grad_x = cv2.Sobel(ch, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(ch, cv2.CV_64F, 0, 1, ksize=3)
        return np.hypot(grad_x, grad_y)

    # Obliczenie gradientów
    edges_l = sobel_edges(l)
    edges_a = sobel_edges(a)
    edges_b = sobel_edges(b)

    # Wektorowa suma gradientowa
    edges_vector_sum = np.sqrt(edges_l**2 + edges_a**2 + edges_b**2)

    # Normalizacja
    edges_vector_sum_norm = cv2.normalize(edges_vector_sum, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Wyświetlenie
    titles = ['Oryginał (RGB)', 'Krawędzie L', 'Krawędzie A', 'Krawędzie B', 'Wektorowa suma krawędzi']
    images = [
        img_rgb,
        cv2.normalize(edges_l, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
        cv2.normalize(edges_a, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
        cv2.normalize(edges_b, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
        edges_vector_sum_norm
    ]

    # Tworzymy figurę
    fig = plt.figure(figsize=(16, 9))  # duży rozmiar, proporcje ekranu
    manager = plt.get_current_fig_manager()

    # Windows
    try:
        manager.window.state('zoomed')  # zmaksymalizowane okno
    except:
        # Linux/Mac - pełen ekran
        manager.full_screen_toggle()

    for i, (im, title) in enumerate(zip(images, titles)):
        plt.subplot(2, 3, i+1)
        plt.imshow(im if im.ndim == 3 else im, cmap=None if im.ndim == 3 else 'gray')
        plt.title(title)
        plt.axis('off')

    plt.tight_layout()
    plt.show()