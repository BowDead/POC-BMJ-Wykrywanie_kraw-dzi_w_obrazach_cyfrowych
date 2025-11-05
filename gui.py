import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from edges_detection import detect_edges

APP_TITLE = "Edge Detection GUI"

root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1600x900")

comparison_frames = []  # lista instancji modułów


# ===== Pomocnicze funkcje =====
def resize_for_canvas(pil_image, frame_size=200):
    w, h = pil_image.size
    scale_ratio = frame_size / max(w, h)
    new_w, new_h = int(w * scale_ratio), int(h * scale_ratio)
    return pil_image.resize((new_w, new_h), Image.LANCZOS)


# ===== Klasa jednego modułu porównania =====
class ComparisonFrame:
    def __init__(self, parent):
        self.cv2_image = None
        self.tk_images = [None] * 5

        # --- główny frame ---
        self.frame = tk.Frame(parent, pady=10, padx=10, bd=2, relief="groove")
        self.frame.pack(side="top", fill="x", padx=10, pady=5)

        # --- pasek górny ---
        top = tk.Frame(self.frame)
        top.pack(fill="x", pady=5)

        self.choose_button = tk.Button(top, text="Wybierz obraz", command=self.choose_image)
        self.choose_button.pack(side="left", padx=5)

        self.color_space_combo = ttk.Combobox(top, state="readonly", width=10)
        self.color_space_combo['values'] = ['RGB', 'HSV', 'LAB']
        self.color_space_combo.current(0)
        self.color_space_combo.pack(side="left", padx=5)

        self.method_combo = ttk.Combobox(top, state="readonly", width=10)
        self.method_combo['values'] = ['Sobel', 'Laplacian', 'Scharr']
        self.method_combo.current(0)
        self.method_combo.pack(side="left", padx=5)

        self.run_button = tk.Button(top, text="Uruchom funkcję", command=self.run_function)
        self.run_button.pack(side="left", padx=5)

        self.status_label = tk.Label(top, text="Nie wczytano obrazu", fg="gray")
        self.status_label.pack(side="left", padx=10)

        # --- obszar na obrazy ---
        self.canvas_frame = tk.Frame(self.frame)
        self.canvas_frame.pack(pady=10)

        self.canvas_list = []
        self.label_list = []

        default_titles = ["Oryginał", "Kanał 1", "Kanał 2", "Kanał 3", "Suma"]

        for i in range(5):
            subframe = tk.Frame(self.canvas_frame)
            subframe.pack(side="left", padx=10)

            canvas = tk.Canvas(subframe, width=200, height=200, bg="#ddd")
            canvas.pack()

            label = tk.Label(subframe, text=default_titles[i])
            label.pack()

            self.canvas_list.append(canvas)
            self.label_list.append(label)

    # --- wybór obrazu ---
    def choose_image(self):
        file_path = filedialog.askopenfilename(title="Wybierz obraz",
                                               filetypes=[("Obrazy", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return

        try:
            img_pil = Image.open(file_path).convert("RGB")
            self.cv2_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            resized = resize_for_canvas(img_pil)
            self.display_image(resized, 0)
            self.status_label.config(text=f"Wczytano: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    # --- wyświetlenie obrazu w kanwie ---
    def display_image(self, pil_image, index):
        frame_size = 200
        pil_resized = resize_for_canvas(pil_image, frame_size)
        img_tk = ImageTk.PhotoImage(pil_resized)
        self.tk_images[index] = img_tk

        canvas = self.canvas_list[index]
        canvas.delete("all")
        x_off = (frame_size - pil_resized.width) // 2
        y_off = (frame_size - pil_resized.height) // 2
        canvas.create_image(x_off, y_off, anchor="nw", image=img_tk)

    # --- uruchomienie funkcji wykrywania ---
    def run_function(self):
        if self.cv2_image is None:
            messagebox.showwarning("Brak obrazu", "Najpierw wybierz obraz!")
            return

        color_space = self.color_space_combo.get()
        method = self.method_combo.get()

        try:
            img_rgb, edges, edges_sum, _ = detect_edges(self.cv2_image, color_space, method)

            img_rgb_pil = Image.fromarray(img_rgb)
            self.display_image(img_rgb_pil, 0)

            color_labels = {
                "RGB": ["R", "G", "B"],
                "HSV": ["H", "S", "V"],
                "LAB": ["L", "A", "B"]
            }.get(color_space, ["Kanał 1", "Kanał 2", "Kanał 3"])

            for i, e in enumerate(edges):
                e_uint8 = (e * 255).astype(np.uint8) if e.max() <= 1 else e.astype(np.uint8)
                edge_pil = Image.fromarray(e_uint8)
                self.display_image(edge_pil, i + 1)
                self.label_list[i + 1].config(text=f"Krawędź {color_labels[i]}")

            e_sum_uint8 = (edges_sum * 255).astype(np.uint8) if edges_sum.max() <= 1 else edges_sum.astype(np.uint8)
            sum_pil = Image.fromarray(e_sum_uint8)
            self.display_image(sum_pil, len(edges) + 1)
            self.label_list[len(edges) + 1].config(text="Suma krawędzi")
            self.label_list[0].config(text="Oryginał")

        except Exception as e:
            messagebox.showerror("Błąd", str(e))


# ===== Funkcje zarządzania modułami =====
def add_comparison():
    frame = ComparisonFrame(scrollable_frame)
    comparison_frames.append(frame)
    update_scroll_region()


def remove_comparison():
    if not comparison_frames:
        return
    last = comparison_frames.pop()
    last.frame.destroy()
    update_scroll_region()


def update_scroll_region(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))


def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# ===== Główny pasek sterowania =====
main_controls = tk.Frame(root, pady=10)
main_controls.pack(fill="x")

tk.Button(main_controls, text="+", command=add_comparison, width=3).pack(side="left", padx=5)
tk.Button(main_controls, text="-", command=remove_comparison, width=3).pack(side="left", padx=5)

# ===== Przewijalna sekcja =====
scroll_container = tk.Frame(root)
scroll_container.pack(fill="both", expand=True)

canvas = tk.Canvas(scroll_container)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

# frame wewnątrz canvasa
scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind("<Configure>", update_scroll_region)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# obsługa przewijania myszką
canvas.bind_all("<MouseWheel>", on_mousewheel)

# start z jednym zestawem
add_comparison()

root.mainloop()
