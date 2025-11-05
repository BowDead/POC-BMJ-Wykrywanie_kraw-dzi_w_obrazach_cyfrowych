import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

from edges_detection import detect_edges

APP_TITLE = "Edge Detection GUI"

cv2_image = None
tk_image = None

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

        frame_size = 300
        scale_ratio = frame_size / max(original_w, original_h)
        new_w, new_h = int(original_w * scale_ratio), int(original_h * scale_ratio)
        img_pil_resized = img_pil.resize((new_w, new_h), Image.LANCZOS)

        cv2_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        tk_image = ImageTk.PhotoImage(img_pil_resized)

        canvas.delete("all")
        x_offset = (frame_size - new_w) // 2
        y_offset = (frame_size - new_h) // 2
        canvas.create_image(x_offset, y_offset, anchor="nw", image=tk_image)

        status_label.config(text=f"Wczytano: {os.path.basename(file_path)}")

    except Exception as e:
        messagebox.showerror("Błąd", str(e))


# ===== Funkcja uruchomienia wykrywania =====
def run_function():
    if cv2_image is None:
        messagebox.showwarning("Brak obrazu", "Najpierw wybierz obraz!")
        return

    color_space = color_space_combo.get()
    method = method_combo.get()

    try:
        img_rgb, edges, edges_sum, titles = detect_edges(cv2_image, color_space, method)

        fig = plt.figure(figsize=(16, 9))
        manager = plt.get_current_fig_manager()
        try:
            manager.window.state('zoomed')   # Windows
        except:
            manager.full_screen_toggle()     # Linux/Mac

        plt.subplot(1, len(edges)+2, 1)
        plt.imshow(img_rgb)
        plt.title("Oryginał")
        plt.axis('off')

        for i, e in enumerate(edges):
            plt.subplot(1, len(edges)+2, i+2)
            plt.imshow(e, cmap='gray')
            plt.title(titles[i])
            plt.axis('off')

        plt.subplot(1, len(edges)+2, len(edges)+2)
        plt.imshow(edges_sum, cmap='gray')
        plt.title("Suma")
        plt.axis('off')

        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Błąd", str(e))


# ===== GUI =====
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("600x500")

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

canvas_frame = tk.Frame(root, width=300, height=300, bg="#ddd")
canvas_frame.pack(expand=True)
canvas_frame.pack_propagate(False)

canvas = tk.Canvas(canvas_frame, width=300, height=300, bg="#ddd")
canvas.pack(expand=True)

status_label = tk.Label(root, text="Nie wczytano obrazu", fg="gray")
status_label.pack(pady=5)

root.mainloop()
