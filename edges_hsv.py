import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_edges_hsv(img):
    """
    Wykrywanie krawędzi w przestrzeni HSV z użyciem operatora Sobela.
    Argument:
        img: obraz wczytany przez cv2.imread() (BGR)
    """
    if img is None:
        raise ValueError("Nieprawidłowy obraz (None).")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(img_hsv)

    def sobel_edges(channel):
        ch = channel.astype(np.float64)
        grad_x = cv2.Sobel(ch, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(ch, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.hypot(grad_x, grad_y)
        mag_norm = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        return mag_norm.astype(np.uint8)

    edges_h = sobel_edges(h)
    edges_s = sobel_edges(s)
    edges_v = sobel_edges(v)

    edges_sum = cv2.max(edges_h, cv2.max(edges_s, edges_v))

    titles = ['Oryginał (RGB)', 'Krawędzie H', 'Krawędzie S', 'Krawędzie V', 'Suma krawędzi']
    images = [img_rgb, edges_h, edges_s, edges_v, edges_sum]

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