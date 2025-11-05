import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from edges_detection import detect_edges

APP_TITLE = "Edge Detection GUI"

cv2_image = None
tk_image = None
preview_images = [None] * 5  # referencje do PhotoImage

# ===== Funkcja wyboru obrazu =====
def choose_image():
    global cv2_image, tk_image
    file_path = filedialog.askopenfilename(title="Wybierz obraz",
                                           filetypes=[("Obrazy", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return

    try:
        img_pil = Image.open(file_path).convert("RGB")
        original_w, original_h = img_pil.size

        frame_size = 250
        scale_ratio = frame_size / max(original_w, original_h)
        new_w, new_h = int(original_w * scale_ratio), int(original_h * scale_ratio)
        img_pil_resized = img_pil.resize((new_w, new_h), Image.LANCZOS)

        cv2_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        tk_image = ImageTk.PhotoImage(img_pil_resized)

        display_image_in_canvas(img_pil_resized, 0)
        status_label.config(text=f"Wczytano: {os.path.basename(file_path)}")

    except Exception as e:
        messagebox.showerror("Błąd", str(e))


# ===== Pomocnicza funkcja do wyświetlania obrazu =====
def display_image_in_canvas(pil_image, index):
    global preview_images
    frame_size = 250

    w, h = pil_image.size
    scale_ratio = frame_size / max(w, h)
    new_w, new_h = int(w * scale_ratio), int(h * scale_ratio)
    pil_resized = pil_image.resize((new_w, new_h), Image.LANCZOS)

    img_tk = ImageTk.PhotoImage(pil_resized)
    preview_images[index] = img_tk  # zapobiega garbage collection

    canvas_list[index].delete("all")
    x_offset = (frame_size - new_w) // 2
    y_offset = (frame_size - new_h) // 2
    canvas_list[index].create_image(x_offset, y_offset, anchor="nw", image=img_tk)


# ===== Funkcja uruchomienia wykrywania =====
def run_function():
    if cv2_image is None:
        messagebox.showwarning("Brak obrazu", "Najpierw wybierz obraz!")
        return

    color_space = color_space_combo.get()
    method = method_combo.get()

    try:
        img_rgb, edges, edges_sum, titles = detect_edges(cv2_image, color_space, method)

        # Oryginał
        img_rgb_pil = Image.fromarray(img_rgb)
        display_image_in_canvas(img_rgb_pil, 0)

        # Dynamiczne etykiety dla systemu barw
        color_labels = {
            "RGB": ["R", "G", "B"],
            "HSV": ["H", "S", "V"],
            "LAB": ["L", "A", "B"]
        }.get(color_space, ["Kanał 1", "Kanał 2", "Kanał 3"])

        # Krawędzie
        for i, e in enumerate(edges):
            e_uint8 = (e * 255).astype(np.uint8) if e.max() <= 1 else e.astype(np.uint8)
            edge_pil = Image.fromarray(e_uint8)
            display_image_in_canvas(edge_pil, i + 1)
            label_list[i + 1].config(text=f"Krawędź {color_labels[i]}")

        # Suma
        e_sum_uint8 = (edges_sum * 255).astype(np.uint8) if edges_sum.max() <= 1 else edges_sum.astype(np.uint8)
        sum_pil = Image.fromarray(e_sum_uint8)
        display_image_in_canvas(sum_pil, len(edges) + 1)
        label_list[len(edges) + 1].config(text="Suma krawędzi")

        # Oryginał
        label_list[0].config(text="Oryginał")

    except Exception as e:
        messagebox.showerror("Błąd", str(e))


# ===== GUI =====
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1600x600")

frame_top = tk.Frame(root, pady=5)
frame_top.pack(fill="x")

choose_button = tk.Button(frame_top, text="Wybierz obraz", command=choose_image)
choose_button.pack(side="left", padx=5)

color_space_combo = ttk.Combobox(frame_top, state="readonly", width=10)
color_space_combo['values'] = ['RGB', 'HSV', 'LAB']
color_space_combo.current(0)
color_space_combo.pack(side="left", padx=5)

method_combo = ttk.Combobox(frame_top, state="readonly", width=10)
method_combo['values'] = ['Sobel', 'Laplacian', 'Scharr']
method_combo.current(0)
method_combo.pack(side="left", padx=5)

run_button = tk.Button(frame_top, text="Uruchom funkcję", command=run_function)
run_button.pack(side="left", padx=5)

# ===== Obszary na obrazy =====
canvas_frame = tk.Frame(root)
canvas_frame.pack(pady=10)

canvas_list = []
label_list = []

default_titles = ["Oryginał", "Kanał 1", "Kanał 2", "Kanał 3", "Suma"]

for i in range(5):
    frame = tk.Frame(canvas_frame)
    frame.pack(side="left", padx=10)

    canvas = tk.Canvas(frame, width=250, height=250, bg="#ddd")
    canvas.pack()

    label = tk.Label(frame, text=default_titles[i])
    label.pack()

    canvas_list.append(canvas)
    label_list.append(label)

status_label = tk.Label(root, text="Nie wczytano obrazu", fg="gray")
status_label.pack(pady=5)

root.mainloop()
