import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
import tkinter as tk

# Okno wyboru pliku
root = tk.Tk()
root.withdraw()
image_path = filedialog.askopenfilename(
    title="Wybierz obraz", 
    filetypes=[("Obrazy", "*.png;*.jpg;*.jpeg")]
)

img = cv2.imread(image_path)
if img is None:
    raise FileNotFoundError(f"Nie znaleziono pliku: {image_path}")

# Konwersje
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

# Rozdzielenie kanałów
l, a, b = cv2.split(img_lab)

# Funkcja Sobel z normalizacją
def sobel_edges(channel):
    ch = channel.astype(np.float64)
    grad_x = cv2.Sobel(ch, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(ch, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.hypot(grad_x, grad_y)
    return magnitude  # zwracamy bez normalizacji — zostanie użyta później

# Gradienty dla każdego kanału
edges_l = sobel_edges(l)
edges_a = sobel_edges(a)
edges_b = sobel_edges(b)

# ✅ Wektorowa suma gradientowa
edges_vector_sum = np.sqrt(edges_l**2 + edges_a**2 + edges_b**2)

# Normalizacja do zakresu 0–255
edges_vector_sum_norm = cv2.normalize(edges_vector_sum, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

# Wizualizacja
titles = [
    'Oryginał (RGB)', 
    'Krawędzie L', 
    'Krawędzie A', 
    'Krawędzie B', 
    'Wektorowa suma krawędzi'
]
images = [
    img_rgb,
    cv2.normalize(edges_l, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
    cv2.normalize(edges_a, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
    cv2.normalize(edges_b, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
    edges_vector_sum_norm
]

plt.figure(figsize=(14, 8))
for i, (im, title) in enumerate(zip(images, titles)):
    plt.subplot(2, 3, i+1)
    if im.ndim == 3:
        plt.imshow(im)
    else:
        plt.imshow(im, cmap='gray', vmin=0, vmax=255)
    plt.title(title)
    plt.axis('off')

plt.tight_layout()
plt.show()
