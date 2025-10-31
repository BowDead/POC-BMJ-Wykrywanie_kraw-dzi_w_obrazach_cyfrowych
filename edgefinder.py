import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from edges_rgb import detect_edges_rgb
from edges_hsv import detect_edges_hsv
from edges_lab import detect_edges_lab

APP_TITLE = "Edge Detection GUI"

# ===== Globalne zmienne =====
cv2_image = None
tk_image = None

# ===== Funkcje =====
def choose_image():
    global cv2_image, tk_image
    file_path = filedialog.askopenfilename(
        title="Wybierz obraz",
        filetypes=[("Obrazy", "*.png;*.jpg;*.jpeg")]
    )
    if not file_path:
        return

    try:
        # Wczytanie obrazu przez Pillow
        img_pil = Image.open(file_path).convert("RGB")

        # Konwersja do formatu OpenCV (BGR)
        cv2_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        # Tworzenie PhotoImage do wyświetlenia w Tkinter
        tk_image = ImageTk.PhotoImage(img_pil)

        # Czyszczenie canvas
        canvas.delete("all")
        canvas.config(scrollregion=(0, 0, tk_image.width(), tk_image.height()))
        canvas.create_image(0, 0, anchor="nw", image=tk_image)

        status_label.config(text=f"Wczytano: {os.path.basename(file_path)}")

    except Exception as e:
        messagebox.showerror("Błąd", str(e))

def run_function():
    if cv2_image is None:
        messagebox.showwarning("Brak obrazu", "Najpierw wybierz obraz!")
        return

    selected = combo.get()
    if not selected:
        messagebox.showwarning("Brak wyboru", "Najpierw wybierz funkcję!")
        return

    try:
        if selected == "Krawędzie RGB":
            detect_edges_rgb(cv2_image)
        elif selected == "Krawędzie HSV":
            detect_edges_hsv(cv2_image)
        elif selected == "Krawędzie LAB":
            detect_edges_lab(cv2_image)
        else:
            messagebox.showerror("Błąd", "Nieznana funkcja!")
    except Exception as e:
        messagebox.showerror("Błąd podczas działania funkcji", str(e))

# ===== GUI =====
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("600x500")

# Ramka do przycisków
frame_top = tk.Frame(root, pady=5)
frame_top.pack(fill="x")

choose_button = tk.Button(frame_top, text="Wybierz obraz", command=choose_image)
choose_button.pack(side="left", padx=5)

combo = ttk.Combobox(frame_top, state="readonly", width=20)
combo['values'] = ["Krawędzie RGB", "Krawędzie HSV", "Krawędzie LAB"]
combo.current(0)
combo.pack(side="left", padx=5)

run_button = tk.Button(frame_top, text="Uruchom funkcję", command=run_function)
run_button.pack(side="left", padx=5)

# Canvas z paskami przewijania
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill="both", expand=True)

h_scroll = tk.Scrollbar(canvas_frame, orient="horizontal")
h_scroll.pack(side="bottom", fill="x")

v_scroll = tk.Scrollbar(canvas_frame, orient="vertical")
v_scroll.pack(side="right", fill="y")

canvas = tk.Canvas(canvas_frame, xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set, bg="#ddd")
canvas.pack(side="left", fill="both", expand=True)

h_scroll.config(command=canvas.xview)
v_scroll.config(command=canvas.yview)

status_label = tk.Label(root, text="Nie wczytano obrazu", fg="gray")
status_label.pack(pady=5)

root.mainloop()
