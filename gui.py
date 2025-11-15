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
shared_image_cv2 = None  # wspólny obraz w formacie cv2
shared_image_pil = None  # wspólny obraz w formacie PIL
shared_image_path = None  # ścieżka do obrazu (dla etykiety)

# ===== FOLDERY DOMYŚLNE =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, "Przykładowe obrazy")
OUTPUT_DIR = os.path.join(BASE_DIR, "Zapisane obrazy wynikowe")

# Tworzymy foldery, jeśli ich nie ma
os.makedirs(SAMPLES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)



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
        self.pil_images = [None] * 5  # zapamiętane obrazy PIL do zapisu
        

        # --- główny frame ---
        self.frame = tk.Frame(parent, pady=10, padx=10, bd=2, relief="groove")
        self.frame.pack(side="top", fill="x", padx=10, pady=5)

        # --- pasek górny ---
        top = tk.Frame(self.frame)
        top.pack(fill="x", pady=5)

        self.color_space_combo = ttk.Combobox(top, state="readonly", width=10)
        self.color_space_combo['values'] = ['RGB', 'HSV', 'LAB']
        self.color_space_combo.current(0)
        self.color_space_combo.pack(side="left", padx=5)

        self.method_combo = ttk.Combobox(top, state="readonly", width=10)
        self.method_combo['values'] = ['Sobel', 'Laplacian', 'Scharr']
        self.method_combo.current(0)
        self.method_combo.pack(side="left", padx=5)

        self.status_label = tk.Label(top, text="Brak obrazu", fg="gray")
        self.status_label.pack(side="left", padx=10)

        # --- obszar na obrazy ---
        self.canvas_frame = tk.Frame(self.frame)
        self.canvas_frame.pack(pady=10)

        self.canvas_list = []
        self.label_list = []
        self.save_buttons = []

        default_titles = ["Oryginał", "Kanał 1", "Kanał 2", "Kanał 3", "Suma"]

        for i in range(5):
            subframe = tk.Frame(self.canvas_frame)
            subframe.pack(side="left", padx=0)

            canvas = tk.Canvas(subframe, width=200, height=200, bg="#ddd")
            canvas.pack()

            label = tk.Label(subframe, text=default_titles[i])
            label.pack()

            save_btn = tk.Button(subframe, text="Zapisz", command=lambda idx=i: self.save_image(idx))
            save_btn.pack(pady=3)

            self.canvas_list.append(canvas)
            self.label_list.append(label)
            self.save_buttons.append(save_btn)

    # --- ustawienie obrazu współdzielonego ---
    def set_shared_image(self, pil_img, cv2_img, file_path):
        self.cv2_image = cv2_img
        self.display_image(resize_for_canvas(pil_img), 0)
        self.pil_images[0] = pil_img
        self.status_label.config(text=f"Wczytano: {os.path.basename(file_path)}", fg="black")

    # --- wyświetlenie obrazu w kanwie ---
    def display_image(self, pil_image, index):
        frame_size = 200
        pil_resized = resize_for_canvas(pil_image, frame_size)
        img_tk = ImageTk.PhotoImage(pil_resized)
        self.tk_images[index] = img_tk
        self.pil_images[index] = pil_image.copy()

        canvas = self.canvas_list[index]
        canvas.delete("all")
        canvas_width = int(canvas["width"])
        canvas_height = int(canvas["height"])
        canvas.create_image(canvas_width // 2 + 2, canvas_height // 2+2, anchor="center", image=img_tk)


    # --- zapisywanie obrazu ---
    def save_image(self, index):
        if self.pil_images[index] is None:
            messagebox.showinfo("Brak obrazu", "Brak obrazu do zapisania.")
            return
        input_filename = os.path.splitext(os.path.basename(shared_image_path))[0];
        label_text = self.label_list[index].cget("text").replace(" ", "_").lower()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile=f"{input_filename}_{label_text}.png",
            initialdir=OUTPUT_DIR,
            title="Zapisz obraz jako"
        )

        if file_path:
            try:
                self.pil_images[index].save(file_path)
                messagebox.showinfo("Sukces", f"Zapisano: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się zapisać obrazu:\n{e}")

    # --- uruchomienie funkcji wykrywania ---
    def run_function(self):
        if self.cv2_image is None:
            self.status_label.config(text="Brak obrazu", fg="red")
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
                e_uint8 = 255 - e_uint8
                # zamiana na czarno-biały (monochromatyczny)
                _, binary = cv2.threshold(e_uint8, 254, 255, cv2.THRESH_BINARY)
        
                # wyświetlanie
                edge_pil = Image.fromarray(binary)
                self.display_image(edge_pil, i + 1)
                self.label_list[i + 1].config(text=f"Krawędź {color_labels[i]}")

            e_sum_uint8 = (edges_sum * 255).astype(np.uint8) if edges_sum.max() <= 1 else edges_sum.astype(np.uint8)
            e_sum_uint8 = 255 - e_sum_uint8
            _, binary = cv2.threshold(e_sum_uint8, 254, 255, cv2.THRESH_BINARY)
        
            # wyświetlanie
            sum_pil = Image.fromarray(binary)
            self.display_image(sum_pil, len(edges) + 1)
            self.label_list[len(edges) + 1].config(text="Suma krawędzi")
            self.label_list[0].config(text="Oryginał")

            self.status_label.config(text="Gotowe", fg="green")

        except Exception as e:
            messagebox.showerror("Błąd", str(e))
            self.status_label.config(text="Błąd", fg="red")


# ===== Funkcje zarządzania modułami =====
def add_comparison():
    frame = ComparisonFrame(scrollable_frame)
    comparison_frames.append(frame)
    # jeśli już mamy obraz, ustaw go w nowej ramce
    if shared_image_pil is not None and shared_image_cv2 is not None:
        frame.set_shared_image(shared_image_pil, shared_image_cv2, shared_image_path)
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


# ===== Główne przyciski =====
main_controls = tk.Frame(root, pady=10)
main_controls.pack(fill="x")

# przyciski zarządzania ramkami
tk.Button(main_controls, text="+", command=add_comparison, width=3).pack(side="left", padx=5)
tk.Button(main_controls, text="-", command=remove_comparison, width=3).pack(side="left", padx=5)

# przycisk wyboru obrazu
def choose_shared_image():
    global shared_image_cv2, shared_image_pil, shared_image_path

    file_path = filedialog.askopenfilename(title="Wybierz obraz",
                                           filetypes=[("Obrazy", "*.png;*.jpg;*.jpeg")],
                                           initialdir=SAMPLES_DIR)
    if not file_path:
        return

    try:
        img_pil = Image.open(file_path).convert("RGB")
        img_cv2 = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        shared_image_cv2 = img_cv2
        shared_image_pil = img_pil
        shared_image_path = file_path

        for frame in comparison_frames:
            frame.set_shared_image(img_pil, img_cv2, file_path)

        image_status_label.config(text=f"Wczytano: {os.path.basename(file_path)}", fg="black")
    except Exception as e:
        messagebox.showerror("Błąd", str(e))


tk.Button(main_controls, text="Wybierz obraz", command=choose_shared_image).pack(side="left", padx=10)

# przycisk uruchom funkcję
def run_all():
    if shared_image_cv2 is None:
        messagebox.showwarning("Brak obrazu", "Najpierw wybierz obraz!")
        return
    for frame in comparison_frames:
        frame.run_function()


tk.Button(main_controls, text="Uruchom funkcję", command=run_all, bg="#4CAF50", fg="white").pack(side="left", padx=10)

image_status_label = tk.Label(main_controls, text="Nie wczytano obrazu", fg="gray")
image_status_label.pack(side="left", padx=10)


# ===== Sekcja przewijana =====
scroll_container = tk.Frame(root)
scroll_container.pack(fill="both", expand=True)

canvas = tk.Canvas(scroll_container)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind("<Configure>", update_scroll_region)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

canvas.bind_all("<MouseWheel>", on_mousewheel)

# start z jedną ramką
add_comparison()

root.mainloop()
