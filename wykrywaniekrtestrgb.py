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

# Konwersja z BGR (OpenCV) na RGB (dla poprawnego wyświetlania)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# === Rozdzielenie na kanały kolorów ===
r, g, b = cv2.split(img_rgb)

# === Wykrywanie krawędzi dla każdego kanału (Sobel) ===
def sobel_edges(channel):
    # Sobel w poziomie i pionie
    grad_x = cv2.Sobel(channel, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(channel, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(grad_x, grad_y)
    magnitude = cv2.convertScaleAbs(magnitude)
    return magnitude

edges_r = sobel_edges(r)
edges_g = sobel_edges(g)
edges_b = sobel_edges(b)

# === Zsumowanie krawędzi z kanałów ===
edges_sum = cv2.addWeighted(edges_r, 1/3, edges_g, 1/3, 0)
edges_sum = cv2.addWeighted(edges_sum, 1, edges_b, 1/3, 0)

# === Wyświetlenie wyników ===
titles = ['Oryginał', 'Krawędzie R', 'Krawędzie G', 'Krawędzie B', 'Suma krawędzi']
images = [img_rgb, edges_r, edges_g, edges_b, edges_sum]

plt.figure(figsize=(12, 8))
for i in range(5):
    plt.subplot(2, 3, i+1)
    plt.imshow(images[i], cmap='gray' if i > 0 else None)
    plt.title(titles[i])
    plt.axis('off')

plt.tight_layout()
plt.show()
