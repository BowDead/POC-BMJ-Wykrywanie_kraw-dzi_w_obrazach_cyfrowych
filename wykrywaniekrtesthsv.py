import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
import tkinter as tk

root = tk.Tk()
root.withdraw()
image_path = filedialog.askopenfilename(title="Wybierz obraz", filetypes=[("Obrazy", "*.png;*.jpg;*.jpeg")])

img = cv2.imread(image_path)
if img is None:
    raise FileNotFoundError(f"Nie znaleziono pliku: {image_path}")

# Konwersje
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)       # do poprawnego wyświetlenia w matplotlib
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)       # do przetwarzania

# Rozdzielenie na kanały (H:0-179, S:0-255, V:0-255)
h, s, v = cv2.split(img_hsv)

# Funkcja Sobel z normalizacją do 0-255 (uint8) do wyświetlenia
def sobel_edges(channel):
    # konwertuj na float dla Sobel
    ch = channel.astype(np.float64)
    grad_x = cv2.Sobel(ch, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(ch, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.hypot(grad_x, grad_y)  # sqrt(gx^2 + gy^2)
    # normalizacja do zakresu 0-255
    mag_norm = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    mag_uint8 = mag_norm.astype(np.uint8)
    return mag_uint8

edges_h = sobel_edges(h)
edges_s = sobel_edges(s)
edges_v = sobel_edges(v)

# Zsumowanie (maksymalna z trzech)
edges_sum = cv2.max(edges_h, cv2.max(edges_s, edges_v))

# Wyświetlanie:
titles = ['Oryginał (RGB)', 'Krawędzie H', 'Krawędzie S', 'Krawędzie V', 'Suma krawędzi']
images = [
    img_rgb,
    edges_h,
    edges_s,
    edges_v,
    edges_sum
]

plt.figure(figsize=(14, 8))
for i, (im, title) in enumerate(zip(images, titles)):
    plt.subplot(2, 3, i+1)
    # jeśli obraz ma 3 wymiary traktuj jako kolor (RGB), inaczej grayscale
    if im.ndim == 3:
        plt.imshow(im)               # RGB już poprawne
    else:
        plt.imshow(im, cmap='gray', vmin=0, vmax=255)
    plt.title(title)
    plt.axis('off')

plt.tight_layout()
plt.show()
