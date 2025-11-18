import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from edges_detection import detect_edges

# ==============================================================================
# 🌎 Obsługa języków
# ==============================================================================

# Aktualny język ('pl' lub 'en')
current_language = 'pl'

# Słownik z tłumaczeniami
TRANSLATIONS = {
    'pl': {
        # Tytuł aplikacji
        'APP_TITLE': "Detekcja Krawędzi GUI",
        # Teksty główne
        'ADD_FRAME': "+",
        'REMOVE_FRAME': "-",
        'CHOOSE_IMAGE': "Wybierz obraz",
        'RUN_FUNCTION': "Uruchom funkcję",
        'IMAGE_NOT_LOADED': "Nie wczytano obrazu",
        'IMAGE_LOADED': "Wczytano: {}", # {} zostanie zastąpione nazwą pliku
        'NO_IMAGE_SELECTED_WARNING': "Najpierw wybierz obraz!",
        # Teksty w module (ComparisonFrame)
        'STATUS_NO_IMAGE': "Brak obrazu",
        'STATUS_READY': "Gotowe",
        'STATUS_ERROR': "Błąd",
        'STATUS_LOADED': "Wczytano: {}",
        'BINARYZATION': "Binaryzacja",
        'ORIGINAL': "Oryginał",
        'EDGE': "Krawędź",
        'EDGE_SUM': "Suma krawędzi",
        'SAVE': "Zapisz",
        'NO_IMAGE_TO_SAVE': "Brak obrazu do zapisania.",
        'SAVE_SUCCESS': "Sukces",
        'SAVED': "Zapisano: {}",
        'SAVE_ERROR': "Nie udało się zapisać obrazu:\n{}",
        'SAVE_AS_TITLE': "Zapisz obraz jako",
        'FILETYPE': "Pliki PNG",
        'UNKNOWN_ERROR': "Błąd",
        # Przyciski przełącznika języka
        'LANGUAGE': "Język:",
        'LANG_PL': "Polski (PL)",
        'LANG_EN': "Angielski (EN)",
        # Tytuły kanałów i błędy z edges_detection.py
        'CHANNEL_R': 'R',
        'CHANNEL_G': 'G',
        'CHANNEL_B': 'B',
        'CHANNEL_H': 'H',
        'CHANNEL_S': 'S',
        'CHANNEL_V': 'V',
        'CHANNEL_L': 'L',
        'CHANNEL_A': 'A',
        'CHANNEL_B': 'B',
        'CHANNEL_C': 'C',
        'CHANNEL_M': 'M',
        'CHANNEL_Y': 'Y',
        'CHANNEL_K': 'K',
        'EDGE_SUM_TITLE': 'Suma krawędzi',
        'INVALID_IMAGE': "Nieprawidłowy obraz (None).",
        'UNKNOWN_METHOD': "Nieznana metoda wykrywania krawędzi.",
        'UNKNOWN_COLOR_SPACE': "Nieznany system kolorów.",
    },
    'en': {
        # Tytuł aplikacji
        'APP_TITLE': "Edge Detection GUI",
        # Teksty główne
        'ADD_FRAME': "+",
        'REMOVE_FRAME': "-",
        'CHOOSE_IMAGE': "Choose Image",
        'RUN_FUNCTION': "Run Function",
        'IMAGE_NOT_LOADED': "No image loaded",
        'IMAGE_LOADED': "Loaded: {}",
        'NO_IMAGE_SELECTED_WARNING': "Please choose an image first!",
        # Teksty w module (ComparisonFrame)
        'STATUS_NO_IMAGE': "No image",
        'STATUS_READY': "Ready",
        'STATUS_ERROR': "Error",
        'STATUS_LOADED': "Loaded: {}",
        'BINARYZATION': "Binarization",
        'ORIGINAL': "Original",
        'EDGE': "Edge",
        'EDGE_SUM': "Edge Sum",
        'SAVE': "Save",
        'NO_IMAGE_TO_SAVE': "No image to save.",
        'SAVE_SUCCESS': "Success",
        'SAVED': "Saved: {}",
        'SAVE_ERROR': "Failed to save image:\n{}",
        'SAVE_AS_TITLE': "Save image as",
        'FILETYPE': "PNG files",
        'UNKNOWN_ERROR': "Error",
        # Przyciski przełącznika języka
        'LANGUAGE': "Language:",
        'LANG_PL': "Polish (PL)",
        'LANG_EN': "English (EN)",
        # Tytuły kanałów i błędy z edges_detection.py
        'CHANNEL_R': 'R',
        'CHANNEL_G': 'G',
        'CHANNEL_B': 'B',
        'CHANNEL_H': 'H',
        'CHANNEL_S': 'S',
        'CHANNEL_V': 'V',
        'CHANNEL_L': 'L',
        'CHANNEL_A': 'A',
        'CHANNEL_B': 'B',
        'CHANNEL_C': 'C',
        'CHANNEL_M': 'M',
        'CHANNEL_Y': 'Y',
        'CHANNEL_K': 'K',
        'EDGE_SUM_TITLE': 'Edge Sum',
        'INVALID_IMAGE': "Invalid image (None).",
        'UNKNOWN_METHOD': "Unknown edge detection method.",
        'UNKNOWN_COLOR_SPACE': "Unknown color space.",
    }
}

def get_text(key):
    """Zwraca tekst dla danego klucza w aktualnym języku."""
    return TRANSLATIONS[current_language].get(key, key)
# ==============================================================================
# Koniec sekcji Języki
# ==============================================================================

root = tk.Tk()
root.title(get_text('APP_TITLE')) # Użycie get_text
root.geometry("1600x900")

root.state("zoomed")

comparison_frames = []
shared_image_cv2 = None
shared_image_pil = None
shared_image_path = None

# ===== FOLDERY DOMYŚLNE =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, "Przykładowe obrazy")
OUTPUT_DIR = os.path.join(BASE_DIR, "Zapisane obrazy wynikowe")

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
        self.tk_images = []
        self.pil_images = []

        # --- główny frame ---
        self.frame = tk.Frame(parent, pady=10, padx=10, bd=2, relief="groove")
        self.frame.pack(side="top", fill="x", padx=10, pady=5)

        # --- pasek górny ---
        top = tk.Frame(self.frame)
        top.pack(fill="x", pady=5)

        self.color_space_combo = ttk.Combobox(top, state="readonly", width=10)
        self.color_space_combo['values'] = ['RGB', 'HSV', 'LAB', 'CMYK']
        self.color_space_combo.current(0)
        self.color_space_combo.pack(side="left", padx=5)

        self.method_combo = ttk.Combobox(top, state="readonly", width=10)
        self.method_combo['values'] = ['Sobel', 'Laplacian', 'Scharr', 'Prewitt']
        self.method_combo.current(0)
        self.method_combo.pack(side="left", padx=5)

        self.status_label = tk.Label(top, text=get_text('STATUS_NO_IMAGE'), fg="gray")
        self.status_label.pack(side="left", padx=10)

        self.binary_var = tk.BooleanVar(value=False)
        self.binary_check = tk.Checkbutton(top, text=get_text('BINARYZATION'), variable=self.binary_var)
        self.binary_check.pack(side="left", padx=10)

        # --- obszar na obrazy ---
        self.canvas_frame = tk.Frame(self.frame)
        self.canvas_frame.pack(pady=10)

        self.canvas_list = []
        self.label_list = []
        self.save_buttons = []

        # Tworzymy tylko jedną kanwę – Oryginał
        self._create_canvas_block(get_text('ORIGINAL'))

    def _create_canvas_block(self, title):
        subframe = tk.Frame(self.canvas_frame)
        subframe.pack(side="left", padx=0)

        canvas = tk.Canvas(subframe, width=200, height=200, bg="#ddd")
        canvas.pack()

        label = tk.Label(subframe, text=title)
        label.pack()

        save_btn = tk.Button(
            subframe,
            text=get_text('SAVE'),
            command=lambda idx=len(self.canvas_list): self.save_image(idx)
        )
        save_btn.pack(pady=3)

        self.canvas_list.append(canvas)
        self.label_list.append(label)
        self.save_buttons.append(save_btn)

    def clear_dynamic_canvases(self):
        # usuwa wszystko poza Oryginałem (index 0)
        for canvas, label, btn in zip(self.canvas_list[1:], self.label_list[1:], self.save_buttons[1:]):
            canvas.master.destroy()

        self.canvas_list = self.canvas_list[:1]
        self.label_list = self.label_list[:1]
        self.save_buttons = self.save_buttons[:1]

    # Nowa metoda do aktualizacji tekstów w ramce
    def update_texts(self):
        self.binary_check.config(text=get_text('BINARYZATION'))

        # Aktualizacja statusu
        if self.cv2_image is None:
            self.status_label.config(text=get_text('STATUS_NO_IMAGE'), fg="gray")
        else:
            # Zachowaj nazwę pliku, jeśli jest wczytany
            status_text = get_text('STATUS_LOADED').format(os.path.basename(shared_image_path))
            self.status_label.config(text=status_text, fg="black")

        # Aktualizacja etykiet i przycisków (dla istniejących bloków)
        self.label_list[0].config(text=get_text('ORIGINAL'))

        # Etykiety dynamiczne zostaną odtworzone poprawnie przy następnym run_function
        for i in range(1, len(self.label_list)):
            label = self.label_list[i]
            btn = self.save_buttons[i]
            if "Suma" in label.cget("text") or "Sum" in label.cget("text"):
                label.config(text=get_text('EDGE_SUM'))
            else: # Etykiety kanałów
                # Tutaj moglibyśmy dodać bardziej skomplikowaną logikę mapowania kanałów
                # ale dla prostoty zostawiamy tylko "Oryginał" i "Sumę" do natychmiastowej zmiany.
                # Etykiety kanałów (np. Krawędź R) są odtwarzane w run_function,
                # które musi zostać wywołane ponownie.
                pass

        for btn in self.save_buttons:
            btn.config(text=get_text('SAVE'))


    # --- ustawienie obrazu współdzielonego ---
    def set_shared_image(self, pil_img, cv2_img, file_path):
        self.cv2_image = cv2_img
        self.display_image(resize_for_canvas(pil_img), 0)
        self.pil_images[0] = pil_img
        status_text = get_text('STATUS_LOADED').format(os.path.basename(file_path))
        self.status_label.config(text=status_text, fg="black")

    # --- wyświetlenie obrazu w kanwie ---
    def display_image(self, pil_image, index):
        frame_size = 200
        pil_resized = resize_for_canvas(pil_image, frame_size)
        img_tk = ImageTk.PhotoImage(pil_resized)

        while len(self.tk_images) <= index:
            self.tk_images.append(None)
        while len(self.pil_images) <= index:
            self.pil_images.append(None)

        self.tk_images[index] = img_tk
        self.pil_images[index] = pil_image.copy()

        canvas = self.canvas_list[index]
        canvas.delete("all")
        canvas_width = int(canvas["width"])
        canvas_height = int(canvas["height"])
        canvas.create_image(canvas_width // 2 + 2, canvas_height // 2+2, anchor="center", image=img_tk)


    # --- zapisywanie obrazu ---
    def save_image(self, index):
        if index >= len(self.pil_images) or self.pil_images[index] is None:
            messagebox.showinfo(get_text('NO_IMAGE_TO_SAVE'), get_text('NO_IMAGE_TO_SAVE'))
            return
        input_filename = os.path.splitext(os.path.basename(shared_image_path))[0];
        label_text = self.label_list[index].cget("text").replace(" ", "_").lower()

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[(get_text('FILETYPE'), "*.png")],
            initialfile=f"{input_filename}_{label_text}.png",
            initialdir=OUTPUT_DIR,
            title=get_text('SAVE_AS_TITLE')
        )

        if file_path:
            try:
                self.pil_images[index].save(file_path)
                messagebox.showinfo(get_text('SAVE_SUCCESS'), get_text('SAVED').format(os.path.basename(file_path)))
            except Exception as e:
                messagebox.showerror(get_text('UNKNOWN_ERROR'), get_text('SAVE_ERROR').format(e))

    # --- uruchomienie funkcji wykrywania ---
    def run_function(self):
        # usuń stare canvas zanim wstawimy nowe
        self.clear_dynamic_canvases()

        if self.cv2_image is None:
            self.status_label.config(text=get_text('STATUS_NO_IMAGE'), fg="red")
            return

        color_space = self.color_space_combo.get()
        method = self.method_combo.get()

        try:
            # Zmiana: przekazujemy funkcję get_text
            img_rgb, edges, edges_sum, titles = detect_edges(self.cv2_image, color_space, method, translations_getter=get_text)

            img_rgb_pil = Image.fromarray(img_rgb)
            self.display_image(img_rgb_pil, 0)

            # Tytuły pochodzą teraz z edges_detection.py, ale musimy je odpowiednio użyć

            # Najpierw twórz dynamiczne canvas
            # Pomijamy tytuł oryginalnego obrazu (index 0) i tytuł sumy (ostatni)
            channel_titles = titles[:-1]

            for i in range(len(channel_titles)):
                # titles[i] to już przetłumaczona nazwa kanału (np. 'R' lub 'H')
                # A tytuł dla etykiety jest złożony z tekstu "Krawędź" + nazwa kanału
                self._create_canvas_block(f"{get_text('EDGE')} {channel_titles[i]}")

            # teraz uzupełnij obrazami
            for i, e in enumerate(edges):
                e_uint8 = (e * 255).astype(np.uint8) if e.max() <= 1 else e.astype(np.uint8)
                e_uint8 = 255 - e_uint8

                if self.binary_var.get():
                    _, processed = cv2.threshold(e_uint8, 254, 255, cv2.THRESH_BINARY)
                else:
                    processed = e_uint8

                edge_pil = Image.fromarray(processed)
                self.display_image(edge_pil, i + 1)

            e_sum_uint8 = (edges_sum * 255).astype(np.uint8) if edges_sum.max() <= 1 else edges_sum.astype(np.uint8)
            e_sum_uint8 = 255 - e_sum_uint8

            if self.binary_var.get():
                _, processed = cv2.threshold(e_sum_uint8, 254, 255, cv2.THRESH_BINARY)
            else:
                processed = e_sum_uint8

            sum_pil = Image.fromarray(processed)

            # Canvas dla sumy (ostatni element z listy titles)
            self._create_canvas_block(titles[-1])
            self.display_image(sum_pil, len(self.canvas_list) - 1)
            self.label_list[0].config(text=get_text('ORIGINAL'))

            self.status_label.config(text=get_text('STATUS_READY'), fg="green")

        except Exception as e:
            messagebox.showerror(get_text('UNKNOWN_ERROR'), str(e))
            self.status_label.config(text=get_text('STATUS_ERROR'), fg="red")


# ===== Funkcje zarządzania modułami =====
def add_comparison():
    frame = ComparisonFrame(scrollable_frame)
    comparison_frames.append(frame)
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

# Funkcja przełączająca język
def switch_language(lang):
    global current_language
    current_language = lang

    # Aktualizacja tytułu głównego okna
    root.title(get_text('APP_TITLE'))

    # Aktualizacja głównego paska sterowania
    add_btn.config(text=get_text('ADD_FRAME'))
    remove_btn.config(text=get_text('REMOVE_FRAME'))
    choose_img_btn.config(text=get_text('CHOOSE_IMAGE'))
    run_all_btn.config(text=get_text('RUN_FUNCTION'))
    lang_label.config(text=get_text('LANGUAGE'))

    # Aktualizacja Comboboxa języków
    lang_combo['values'] = [get_text('LANG_PL'), get_text('LANG_EN')]
    if lang == 'pl':
        lang_var.set(get_text('LANG_PL'))
    else:
        lang_var.set(get_text('LANG_EN'))

    # Aktualizacja statusu ładowania obrazu
    if shared_image_cv2 is None:
        image_status_label.config(text=get_text('IMAGE_NOT_LOADED'), fg="gray")
    else:
        text = get_text('IMAGE_LOADED').format(os.path.basename(shared_image_path))
        image_status_label.config(text=text, fg="black")

    # Aktualizacja wszystkich instancji modułów
    for frame in comparison_frames:
        frame.update_texts()


# ===== Główne przyciski =====
main_controls = tk.Frame(root, pady=10)
main_controls.pack(fill="x")

# przyciski zarządzania ramkami
add_btn = tk.Button(main_controls, text=get_text('ADD_FRAME'), command=add_comparison, width=3)
add_btn.pack(side="left", padx=5)
remove_btn = tk.Button(main_controls, text=get_text('REMOVE_FRAME'), command=remove_comparison, width=3)
remove_btn.pack(side="left", padx=5)

# przycisk wyboru obrazu
def choose_shared_image():
    global shared_image_cv2, shared_image_pil, shared_image_path

    file_path = filedialog.askopenfilename(title=get_text('CHOOSE_IMAGE'),
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

        text = get_text('IMAGE_LOADED').format(os.path.basename(file_path))
        image_status_label.config(text=text, fg="black")
    except Exception as e:
        messagebox.showerror(get_text('UNKNOWN_ERROR'), str(e))


choose_img_btn = tk.Button(main_controls, text=get_text('CHOOSE_IMAGE'), command=choose_shared_image)
choose_img_btn.pack(side="left", padx=10)

# przycisk uruchom funkcję
def run_all():
    if shared_image_cv2 is None:
        messagebox.showwarning(get_text('IMAGE_NOT_LOADED'), get_text('NO_IMAGE_SELECTED_WARNING'))
        return
    for frame in comparison_frames:
        frame.run_function()


run_all_btn = tk.Button(main_controls, text=get_text('RUN_FUNCTION'), command=run_all, bg="#4CAF50", fg="white")
run_all_btn.pack(side="left", padx=10)

image_status_label = tk.Label(main_controls, text=get_text('IMAGE_NOT_LOADED'), fg="gray")
image_status_label.pack(side="left", padx=10)

# Przełącznik języka
lang_frame = tk.Frame(main_controls)
lang_frame.pack(side="right", padx=10)

lang_label = tk.Label(lang_frame, text=get_text('LANGUAGE'))
lang_label.pack(side="left")

# Zmienna do przechowywania wybranego języka w Comboboxie
lang_var = tk.StringVar(value=get_text('LANG_PL'))

lang_combo = ttk.Combobox(
    lang_frame,
    textvariable=lang_var,
    state="readonly",
    width=15
)
lang_combo['values'] = [get_text('LANG_PL'), get_text('LANG_EN')]
lang_combo.pack(side="left")

# Funkcja obsługująca zmianę w comboboxie
def language_changed(event):
    selected = lang_var.get()
    if selected == get_text('LANG_PL'):
        switch_language('pl')
    elif selected == get_text('LANG_EN'):
        switch_language('en')

lang_combo.bind('<<ComboboxSelected>>', language_changed)


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