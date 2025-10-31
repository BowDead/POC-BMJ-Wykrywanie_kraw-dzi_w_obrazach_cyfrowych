import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_edges_rgb(img):
    """
    Wykrywanie krawędzi w przestrzeni RGB z użyciem operatora Sobela.
    Argument:
        img: obraz wczytany przez cv2.imread() (BGR)
    """
    if img is None:
        raise ValueError("Nieprawidłowy obraz (None).")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    r, g, b = cv2.split(img_rgb)

    def sobel_edges(channel):
        grad_x = cv2.Sobel(channel, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(channel, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = cv2.magnitude(grad_x, grad_y)
        return cv2.convertScaleAbs(magnitude)

    edges_r = sobel_edges(r)
    edges_g = sobel_edges(g)
    edges_b = sobel_edges(b)

    edges_sum = cv2.addWeighted(edges_r, 1/3, edges_g, 1/3, 0)
    edges_sum = cv2.addWeighted(edges_sum, 1, edges_b, 1/3, 0)

    titles = ['Oryginał', 'Krawędzie R', 'Krawędzie G', 'Krawędzie B', 'Suma krawędzi']
    images = [img_rgb, edges_r, edges_g, edges_b, edges_sum]

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