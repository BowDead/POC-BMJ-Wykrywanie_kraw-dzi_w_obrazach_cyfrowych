import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import ctypes

from edges_detection import detect_edges

# Włączenie świadomości DPI dla Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

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
        'IMAGE_LOADED': "Wczytano: {}",
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
        'CHANNEL_R': 'R', 'CHANNEL_G': 'G', 'CHANNEL_B': 'B',
        'CHANNEL_H': 'H', 'CHANNEL_S': 'S', 'CHANNEL_V': 'V',
        'CHANNEL_L': 'L', 'CHANNEL_A': 'A', 'CHANNEL_B': 'B',
        'CHANNEL_C': 'C', 'CHANNEL_M': 'M', 'CHANNEL_Y': 'Y', 'CHANNEL_K': 'K',
        'EDGE_SUM_TITLE': 'Suma krawędzi',
        # Globalne ustawienia
        'GLOBAL_COLOR_SPACE': 'Globalna przestrzeń barw',
        'GLOBAL_METHOD': 'Globalna metoda',
        'APPLY_COLOR_ALL': 'Zastosuj przestrzeń do wszystkich',
        'APPLY_METHOD_ALL': 'Zastosuj metodę do wszystkich',
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
        'CHANNEL_R': 'R', 'CHANNEL_G': 'G', 'CHANNEL_B': 'B',
        'CHANNEL_H': 'H', 'CHANNEL_S': 'S', 'CHANNEL_V': 'V',
        'CHANNEL_L': 'L', 'CHANNEL_A': 'A', 'CHANNEL_B': 'B',
        'CHANNEL_C': 'C', 'CHANNEL_M': 'M', 'CHANNEL_Y': 'Y', 'CHANNEL_K': 'K',
        'EDGE_SUM_TITLE': 'Edge Sum',
        # Global settings
        'GLOBAL_COLOR_SPACE': 'Global color space',
        'GLOBAL_METHOD': 'Global method',
        'APPLY_COLOR_ALL': 'Apply color space to all',
        'APPLY_METHOD_ALL': 'Apply method to all',
    }
}

def get_text(key):
    """Zwraca tekst dla danego klucza w aktualnym języku."""
    return TRANSLATIONS[current_language].get(key, key)
# ==============================================================================
# Koniec sekcji Języki
# ==============================================================================

root = tk.Tk()
root.title(get_text('APP_TITLE')) # Zmiana

# Pobranie rozdzielczości ekranu i ustalenie skali
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Obliczenie skali DPI
dpi = root.winfo_fpixels('1i')
scale_factor = dpi / 96.0  # 96 DPI to standard

# Rozmiar canvas dostosowany do skali
CANVAS_SIZE = int(200 * max(1.0, scale_factor * 0.7))  # Zwiększamy bazowy rozmiar dla wysokiego DPI

# Ustawienie czcionek skalowanych
default_font_size = int(9 * max(1.0, scale_factor * 0.8))
button_font_size = int(9 * max(1.0, scale_factor * 0.8))
label_font_size = int(8 * max(1.0, scale_factor * 0.8))

root.option_add('*Font', f'TkDefaultFont {default_font_size}')
root.option_add('*Button.Font', f'TkDefaultFont {button_font_size}')
root.option_add('*Label.Font', f'TkDefaultFont {label_font_size}')

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
def resize_for_canvas(pil_image, frame_size=None):
    if frame_size is None:
        frame_size = CANVAS_SIZE
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
        self.persistent_windows = []

        # --- główny frame ---
        pady_val = int(10 * max(1.0, scale_factor * 0.7))
        padx_val = int(10 * max(1.0, scale_factor * 0.7))
        self.frame = tk.Frame(parent, pady=pady_val, padx=padx_val, bd=2, relief="groove")
        self.frame.pack(side="top", fill="x", padx=padx_val, pady=int(5 * max(1.0, scale_factor * 0.7)))

        # --- pasek górny ---
        top = tk.Frame(self.frame)
        top.pack(fill="x", pady=int(5 * max(1.0, scale_factor * 0.7)))

        combo_width = int(10 * max(1.0, scale_factor * 0.6))
        self.color_space_combo = ttk.Combobox(top, state="readonly", width=combo_width)
        self.color_space_combo['values'] = ['RGB', 'HSV', 'LAB', 'CMYK']
        self.color_space_combo.current(0)
        self.color_space_combo.pack(side="left", padx=int(5 * max(1.0, scale_factor * 0.7)))

        method_combo_width = int(25 * max(1.0, scale_factor * 0.6))
        self.method_combo = ttk.Combobox(top, state="readonly", width=method_combo_width)
        self.method_combo['values'] = [
            'Sobel',
            'Sobel CV2',
            'Laplacian 4-neighbor',
            'Laplacian 8-neighbor',
            'Laplacian LoG',
            'Scharr',
            'Prewitt',
            'Canny',
            'Canny CV2',
            'Roberts'
        ]
        self.method_combo.current(0)
        self.method_combo.pack(side="left", padx=int(5 * max(1.0, scale_factor * 0.7)))
        
        # Tooltip dla maski metody
        self.tooltip_window = None
        self.method_combo.bind("<Enter>", self.show_mask_tooltip)
        self.method_combo.bind("<Leave>", self.hide_mask_tooltip)

        # --- spinboxy progów filtrów ---
        self.low_threshold = tk.IntVar(value=0)
        self.high_threshold = tk.IntVar(value=255)

        spinbox_width = int(5 * max(1.0, scale_factor * 0.7))
        padx_small = int(3 * max(1.0, scale_factor * 0.7))
        padx_medium = int(10 * max(1.0, scale_factor * 0.7))
        
        tk.Label(top, text="Low T:").pack(side="left", padx=padx_small)
        self.low_spin = tk.Spinbox(top, from_=0, to=255, width=spinbox_width, textvariable=self.low_threshold)
        self.low_spin.pack(side="left", padx=padx_small)

        tk.Label(top, text="High T:").pack(side="left", padx=padx_small)
        self.high_spin = tk.Spinbox(top, from_=1, to=255, width=spinbox_width, textvariable=self.high_threshold)
        self.high_spin.pack(side="left", padx=padx_small)

        self.status_label = tk.Label(top, text=get_text('STATUS_NO_IMAGE'), fg="gray") # Zmiana
        self.status_label.pack(side="left", padx=padx_medium)

        self.binary_var = tk.BooleanVar(value=False)
        self.binary_check = tk.Checkbutton(top, text=get_text('BINARYZATION'), variable=self.binary_var) # Zmiana
        self.binary_check.pack(side="left", padx=padx_medium)
        
        # Przycisk usuwania tej ramki (minus na ramce)
        btn_width = int(3 * max(1.0, scale_factor * 0.7))
        self.remove_btn = tk.Button(top, text=get_text('REMOVE_FRAME'), width=btn_width, command=self.remove_self)
        self.remove_btn.pack(side="right", padx=int(5 * max(1.0, scale_factor * 0.7)))
        

        # --- obszar na obrazy ---
        self.canvas_frame = tk.Frame(self.frame)
        self.canvas_frame.pack(pady=10, anchor="w", fill="x")

        self.canvas_list = []
        self.label_list = []
        self.save_buttons = []

        # Tworzymy tylko jedną kanwę – Oryginał
        self._create_canvas_block(get_text('ORIGINAL')) # Zmiana

        self.preview_window = None

    def _create_canvas_block(self, title):
        subframe = tk.Frame(self.canvas_frame)
        subframe.pack(side="left", padx=int(5 * max(1.0, scale_factor * 0.7)), anchor="w")

        canvas = tk.Canvas(subframe, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="#ddd")
        canvas.pack()

        # Zmień kursor na pointer
        subframe.config(cursor="hand2")

        # Bind kliknięcia, przeciągania i puszczenia
        subframe.bind("<ButtonPress-1>", lambda e, idx=len(self.canvas_list): self.show_preview(e, idx))
        subframe.bind("<ButtonRelease-1>", lambda e: self.hide_preview())
        # Kliknięcie prawym przyciskiem – trwałe okno z obrazem
        subframe.bind("<Button-3>", lambda e, idx=len(self.canvas_list): self.open_persistent_window(idx))

        # Przekierowanie eventów z canvasa
        canvas.bind("<ButtonPress-1>", lambda e: subframe.event_generate("<ButtonPress-1>"))
        # canvas.bind("<B1-Motion>", lambda e: subframe.event_generate("<B1-Motion>"))
        canvas.bind("<ButtonRelease-1>", lambda e: subframe.event_generate("<ButtonRelease-1>"))
        canvas.bind("<Button-3>", lambda e: subframe.event_generate("<Button-3>"))

        label = tk.Label(subframe, text=title)
        label.pack()

        save_btn = tk.Button(
            subframe,
            text=get_text('SAVE'), # Zmiana
            command=lambda idx=len(self.canvas_list): self.save_image(idx)
        )
        save_btn.pack(pady=int(3 * max(1.0, scale_factor * 0.7)))

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
        # Zaktualizuj etykiety stałe
        self.binary_check.config(text=get_text('BINARYZATION'))

        # Aktualizacja statusu
        if self.cv2_image is None:
            self.status_label.config(text=get_text('STATUS_NO_IMAGE'), fg="gray")
        else:
            status_text = get_text('STATUS_LOADED').format(os.path.basename(shared_image_path))
            self.status_label.config(text=status_text, fg="black")

        # Aktualizacja etykiet i przycisków (dla istniejących bloków)
        self.label_list[0].config(text=get_text('ORIGINAL'))

        # Etykiety dynamiczne
        for i in range(1, len(self.label_list)):
            label = self.label_list[i]
            btn = self.save_buttons[i]
            if "Suma" in label.cget("text") or "Sum" in label.cget("text"):
                label.config(text=get_text('EDGE_SUM'))
            else:
                # Wymaga ponownego uruchomienia run_function dla poprawnych nazw kanałów.
                # Tymczasowo, przy zmianie języka, etykieta pozostanie w starym języku + nowy język kanału.
                pass

        for btn in self.save_buttons:
            btn.config(text=get_text('SAVE'))

        # Aktualizuj przycisk usuwania ramki
        try:
            self.remove_btn.config(text=get_text('REMOVE_FRAME'))
        except Exception:
            pass


    # --- ustawienie obrazu współdzielonego ---
    def set_shared_image(self, pil_img, cv2_img, file_path):
        self.cv2_image = cv2_img
        self.display_image(resize_for_canvas(pil_img), 0)
        self.pil_images[0] = pil_img
        self.status_label.config(text=get_text('STATUS_LOADED').format(os.path.basename(file_path)), fg="black") # Zmiana

    # --- wyświetlenie obrazu w kanwie ---
    def display_image(self, pil_image, index):
        pil_resized = resize_for_canvas(pil_image, CANVAS_SIZE)
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
            messagebox.showinfo(get_text("NO_IMAGE_TO_SAVE"), get_text("NO_IMAGE_TO_SAVE")) # Zmiana
            return
        input_filename = os.path.splitext(os.path.basename(shared_image_path))[0];
        label_text = self.label_list[index].cget("text").replace(" ", "_").lower()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[(get_text("FILETYPE"), "*.png")], # Zmiana
            initialfile=f"{input_filename}_{label_text}.png",
            initialdir=OUTPUT_DIR,
            title=get_text("SAVE_AS_TITLE") # Zmiana
        )

        if file_path:
            try:
                self.pil_images[index].save(file_path)
                messagebox.showinfo(get_text("SAVE_SUCCESS"), get_text("SAVED").format(os.path.basename(file_path))) # Zmiana
            except Exception as e:
                messagebox.showerror(get_text("UNKNOWN_ERROR"), get_text("SAVE_ERROR").format(e)) # Zmiana

    # --- uruchomienie funkcji wykrywania ---
    def run_function(self):
        self.clear_dynamic_canvases()

        if self.cv2_image is None:
            self.status_label.config(text=get_text("STATUS_NO_IMAGE"), fg="red") # Zmiana
            return

        color_space = self.color_space_combo.get()
        method = self.method_combo.get()

        low_t = int(self.low_threshold.get())
        high_t = int(self.high_threshold.get())

        try:
            # Zmiana: przekazujemy funkcję get_text
            img_rgb, edges, edges_sum, titles = detect_edges(
                self.cv2_image,
                color_space,
                method,
                translations_getter=get_text,
                low_threshold=low_t,
                high_threshold=high_t
            )

            img_rgb_pil = Image.fromarray(img_rgb)
            self.display_image(img_rgb_pil, 0)

            # Tytuły pochodzą teraz z edges_detection.py, titles zawiera [Kanał 1, Kanał 2, Kanał 3, Suma]
            channel_titles = titles[:-1] # Pomijamy tytuł sumy

            # Najpierw twórz dynamiczne canvas
            for i in range(len(channel_titles)):
                # titles[i] to już przetłumaczona nazwa kanału (np. 'R' lub 'H')
                self._create_canvas_block(f"{get_text('EDGE')} {channel_titles[i]}") # Zmiana

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
            self.label_list[0].config(text=get_text("ORIGINAL")) # Zmiana

            self.status_label.config(text=get_text("STATUS_READY"), fg="green") # Zmiana

        except Exception as e:
            messagebox.showerror(get_text("UNKNOWN_ERROR"), str(e)) # Zmiana
            self.status_label.config(text=get_text("STATUS_ERROR"), fg="red") # Zmiana

    def show_preview(self, event, index):
        if index >= len(self.pil_images) or self.pil_images[index] is None:
            return

        self.hide_preview()

        img = self.pil_images[index]

        canvas = self.canvas_list[index]
        zoom_w, zoom_h = int(canvas["width"]) * 3, int(canvas["height"]) * 3

        # Zmiana: zmniejszamy obraz o kilka px aby uniknąć ucięcia
        zoom_w -= 10
        zoom_h -= 10

        zoomed = img.resize((zoom_w, zoom_h), Image.LANCZOS)
        self.preview_img_tk = ImageTk.PhotoImage(zoomed)

        self.preview_window = tk.Toplevel()
        self.preview_window.overrideredirect(True)
        self.preview_window.attributes("-topmost", True)

        outer_frame = tk.Frame(self.preview_window, bg="black", bd=2)
        outer_frame.pack(padx=2, pady=2)

        inner_frame = tk.Frame(outer_frame, bg="white", bd=2)
        inner_frame.pack(padx=2, pady=2)

        label = tk.Label(inner_frame, image=self.preview_img_tk, borderwidth=0, bg="white")
        label.pack()

        # Zmiana: uwzględnienie marginesów (8 px → 20 px)
        window_w = zoom_w + 20
        window_h = zoom_h + 20

        screen_w = self.preview_window.winfo_screenwidth()
        screen_h = self.preview_window.winfo_screenheight()

        center_x = (screen_w - window_w) // 2
        center_y = (screen_h - window_h) // 2

        self.preview_window.geometry(f"{window_w}x{window_h}+{center_x}+{center_y}")
        self.preview_window.update_idletasks()


    def hide_preview(self):
        """Usuwa okno podglądu."""
        if self.preview_window:
            self.preview_window.destroy()
            self.preview_window = None

    def open_persistent_window(self, index):
        """Otwiera trwałe okno z wybranym obrazem (prawy klik)."""
        if index >= len(self.pil_images) or self.pil_images[index] is None:
            return

        img = self.pil_images[index]

        # Użyj tych samych wymiarów co tymczasowy podgląd (3x canvas - 10px)
        canvas = self.canvas_list[index]
        zoom_w, zoom_h = int(canvas["width"]) * 3, int(canvas["height"]) * 3
        zoom_w -= 10
        zoom_h -= 10
        zoomed = img.resize((zoom_w, zoom_h), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(zoomed)

        win = tk.Toplevel(root)
        label_text = self.label_list[index].cget("text") if index < len(self.label_list) else ""

        # Złóż tytuł z właściwości obrazu / ustawień
        base_name = os.path.splitext(os.path.basename(shared_image_path))[0] if shared_image_path else ""
        cs = self.color_space_combo.get() if hasattr(self, 'color_space_combo') else ""
        method = self.method_combo.get() if hasattr(self, 'method_combo') else ""
        try:
            lt = int(self.low_threshold.get())
            ht = int(self.high_threshold.get())
        except Exception:
            lt, ht = 0, 255
        bin_flag = 1 if self.binary_var.get() else 0

        title_parts = []
        if base_name:
            title_parts.append(base_name)
        if label_text:
            title_parts.append(label_text)
        if cs:
            title_parts.append(cs)
        if method:
            title_parts.append(method)
        title_parts.append(f"LT:{lt} HT:{ht}")
        title_parts.append(f"Bin:{bin_flag}")

        title_str = " | ".join(title_parts) if title_parts else get_text('APP_TITLE')
        try:
            win.title(title_str)
        except Exception:
            pass

        # Ustaw jako okno podrzędne, aby zawsze było nad aplikacją, ale nie nad innymi programami
        try:
            win.transient(root)
            win.lift(root)
        except Exception:
            pass
        win.attributes("-topmost", False)

        # Ramka i label na obraz
        outer = tk.Frame(win, bg="black", bd=2)
        outer.pack(padx=2, pady=2)
        inner = tk.Frame(outer, bg="white", bd=2)
        inner.pack(padx=2, pady=2)
        lbl = tk.Label(inner, image=imgtk, borderwidth=0, bg="white")
        lbl.pack()

        # Wyśrodkuj okno na ekranie podobnie jak podgląd
        try:
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
        except Exception:
            screen_w, screen_h = 1280, 800
        try:
            window_w = zoom_w + 20
            window_h = zoom_h + 20
            center_x = (screen_w - window_w) // 2
            center_y = (screen_h - window_h) // 2
            win.geometry(f"{window_w}x{window_h}+{center_x}+{center_y}")
        except Exception:
            pass

        # Zachowaj referencję, aby obraz nie został zebrany przez GC
        win._imgtk = imgtk
        self.persistent_windows.append(win)

        # Zablokuj możliwość zmiany rozmiaru okna kursorem
        try:
            win.resizable(False, False)
            win.update_idletasks()
            fixed_w = win.winfo_width()
            fixed_h = win.winfo_height()
            win.minsize(fixed_w, fixed_h)
            win.maxsize(fixed_w, fixed_h)
        except Exception:
            pass
    
    def get_mask_visualization(self, method):
        """Tworzy wizualizację maski dla danej metody."""
        masks = {
            'Sobel': [
                (np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]), "Gx"),
                (np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]), "Gy")
            ],
            'Sobel CV2': [
                (np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]), "Gx"),
                (np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]), "Gy")
            ],
            'Laplacian 4-neighbor': [
                (np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]), "4-neighbor")
            ],
            'Laplacian 8-neighbor': [
                (np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]]), "8-neighbor")
            ],
            'Laplacian LoG': [
                (np.array([[0, 0, -1, 0, 0], [0, -1, -2, -1, 0], [-1, -2, 16, -2, -1], 
                          [0, -1, -2, -1, 0], [0, 0, -1, 0, 0]]), "LoG 5x5")
            ],
            'Scharr': [
                (np.array([[-3, 0, 3], [-10, 0, 10], [-3, 0, 3]]), "Gx"),
                (np.array([[-3, -10, -3], [0, 0, 0], [3, 10, 3]]), "Gy")
            ],
            'Prewitt': [
                (np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]), "Gx"),
                (np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]]), "Gy")
            ],
            'Roberts': [
                (np.array([[1, 0], [0, -1]]), "Gx"),
                (np.array([[0, 1], [-1, 0]]), "Gy")
            ],
            'Canny': [
                (np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]), "Sobel Gx"),
                (np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]), "Sobel Gy")
            ],
            'Canny CV2': [
                (np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]), "Sobel Gx"),
                (np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]), "Sobel Gy")
            ]
        }
        
        return masks.get(method, [])
    
    def show_mask_tooltip(self, event):
        """Pokazuje tooltip z wizualizacją maski."""
        method = self.method_combo.get()
        masks = self.get_mask_visualization(method)
        
        if not masks:
            return
        
        # Ukryj stary tooltip jeśli istnieje
        self.hide_mask_tooltip()
        
        # Stwórz okno tooltip
        self.tooltip_window = tk.Toplevel()
        self.tooltip_window.overrideredirect(True)
        self.tooltip_window.attributes("-topmost", True)
        
        # Ramka z ciemnym obramowaniem
        outer_frame = tk.Frame(self.tooltip_window, bg="black", bd=1)
        outer_frame.pack(padx=1, pady=1)
        
        inner_frame = tk.Frame(outer_frame, bg="white", bd=3)
        inner_frame.pack(padx=2, pady=2)
        
        # Tytuł
        title_label = tk.Label(inner_frame, text=f"Maska: {method}", 
                               font=("TkDefaultFont", int(10 * max(1.0, scale_factor * 0.8)), "bold"),
                               bg="white")
        title_label.pack(pady=(5, 10))
        
        # Dla każdej maski (Gx, Gy, etc.)
        for mask_array, mask_name in masks:
            mask_frame = tk.Frame(inner_frame, bg="white")
            mask_frame.pack(pady=5)
            
            # Nazwa maski (Gx, Gy)
            name_label = tk.Label(mask_frame, text=mask_name, 
                                 font=("TkDefaultFont", int(9 * max(1.0, scale_factor * 0.8)), "bold"),
                                 bg="white")
            name_label.pack()
            
            # Wizualizacja maski
            cell_size = 40
            rows, cols = mask_array.shape
            
            canvas = tk.Canvas(mask_frame, width=cols * cell_size, height=rows * cell_size, 
                             bg="white", highlightthickness=0)
            canvas.pack(pady=5)
            
            # Normalizacja do kolorów
            mask_min = mask_array.min()
            mask_max = mask_array.max()
            
            for i in range(rows):
                for j in range(cols):
                    val = mask_array[i, j]
                    
                    # Kolor: czerwony dla ujemnych, zielony dla dodatnich, biały dla 0
                    if val < 0:
                        intensity = int(255 * abs(val - mask_min) / (abs(mask_min) + 1e-10))
                        color = f"#{intensity:02x}{0:02x}{0:02x}"
                        text_color = "white"
                    elif val > 0:
                        intensity = int(255 * val / (mask_max + 1e-10))
                        color = f"#{0:02x}{intensity:02x}{0:02x}"
                        text_color = "white"
                    else:
                        color = "#ffffff"
                        text_color = "black"
                    
                    x1, y1 = j * cell_size, i * cell_size
                    x2, y2 = x1 + cell_size, y1 + cell_size
                    
                    # Rysuj komórkę
                    canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1)
                    
                    # Dodaj tekst z wartością
                    canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, 
                                     text=str(int(val)) if val == int(val) else f"{val:.1f}",
                                     font=("TkDefaultFont", int(11 * max(1.0, scale_factor * 0.8)), "bold"),
                                     fill=text_color)
        
        # Pozycja tooltip
        x = self.method_combo.winfo_rootx() + 10
        y = self.method_combo.winfo_rooty() + self.method_combo.winfo_height() + 5
        
        self.tooltip_window.geometry(f"+{x}+{y}")
        self.tooltip_window.update_idletasks()
    
    def hide_mask_tooltip(self, event=None):
        """Ukrywa tooltip z maską."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def remove_self(self):
        """Usuwa tę instancję ComparisonFrame z listy i GUI."""
        try:
            comparison_frames.remove(self)
        except ValueError:
            pass
        # Zamknij okna trwałe powiązane z tą ramką
        try:
            for w in getattr(self, 'persistent_windows', []):
                try:
                    if w and w.winfo_exists():
                        w.destroy()
                except Exception:
                    pass
            if hasattr(self, 'persistent_windows'):
                self.persistent_windows.clear()
        except Exception:
            pass
        try:
            self.frame.destroy()
        except Exception:
            pass
        update_scroll_region()

# ===== Funkcje zarządzania modułami =====
def add_comparison():
    frame = ComparisonFrame(scrollable_frame)
    comparison_frames.append(frame)
    if shared_image_pil is not None and shared_image_cv2 is not None:
        frame.set_shared_image(shared_image_pil, shared_image_cv2, shared_image_path)
    # Ustaw domyślne wartości z globalnych comboboxów dla nowej ramki
    try:
        frame.color_space_combo.set(global_color_space_var.get())
        frame.method_combo.set(global_method_var.get())
    except Exception:
        pass
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
    # On Windows event.delta > 0 means wheel up. When there's only one box,
    # ignore upward scrolling to prevent moving the view above the single box.
    try:
        if len(comparison_frames) <= 1 and event.delta > 0:
            return
    except Exception:
        pass

    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

# Funkcja przełączająca język
def switch_language(lang):
    global current_language
    current_language = lang

    # Aktualizacja tytułu głównego okna
    root.title(get_text('APP_TITLE'))

    # Aktualizacja głównego paska sterowania
    add_btn.config(text=get_text('ADD_FRAME'))
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

    # Aktualizacja globalnych etykiet i przycisków
    try:
        global_color_label.config(text=get_text('GLOBAL_COLOR_SPACE'))
        global_method_label.config(text=get_text('GLOBAL_METHOD'))
        apply_color_btn.config(text=get_text('APPLY_COLOR_ALL'))
        apply_method_btn.config(text=get_text('APPLY_METHOD_ALL'))
    except Exception:
        pass


# ===== Główne przyciski (Zmienione, aby umożliwić aktualizację tekstu) =====
main_pady = int(10 * max(1.0, scale_factor * 0.7))
main_controls = tk.Frame(root, pady=main_pady)
main_controls.pack(fill="x")

# przyciski zarządzania ramkami
btn_width = int(3 * max(1.0, scale_factor * 0.7))
add_btn = tk.Button(main_controls, text=get_text('ADD_FRAME'), command=add_comparison, width=btn_width)
add_btn.pack(side="left", padx=int(5 * max(1.0, scale_factor * 0.7)))

# przycisk wyboru obrazu
def choose_shared_image():
    global shared_image_cv2, shared_image_pil, shared_image_path

    file_path = filedialog.askopenfilename(title=get_text('CHOOSE_IMAGE'), # Zmiana
                                           filetypes=[(get_text('FILETYPE'), "*.png;*.jpg;*.jpeg")], # Zmiana
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

        image_status_label.config(text=get_text('IMAGE_LOADED').format(os.path.basename(file_path)), fg="black") # Zmiana
    except Exception as e:
        messagebox.showerror(get_text('UNKNOWN_ERROR'), str(e)) # Zmiana


choose_img_btn = tk.Button(main_controls, text=get_text('CHOOSE_IMAGE'), command=choose_shared_image) # Zmiana
choose_img_btn.pack(side="left", padx=int(10 * max(1.0, scale_factor * 0.7)))

# przycisk uruchom funkcję
def run_all():
    if shared_image_cv2 is None:
        messagebox.showwarning(get_text('IMAGE_NOT_LOADED'), get_text('NO_IMAGE_SELECTED_WARNING')) # Zmiana
        return
    for frame in comparison_frames:
        frame.run_function()


run_all_btn = tk.Button(main_controls, text=get_text('RUN_FUNCTION'), command=run_all, bg="#4CAF50", fg="white") # Zmiana
run_all_btn.pack(side="left", padx=int(10 * max(1.0, scale_factor * 0.7)))

image_status_label = tk.Label(main_controls, text=get_text('IMAGE_NOT_LOADED'), fg="gray") # Zmiana
image_status_label.pack(side="left", padx=int(10 * max(1.0, scale_factor * 0.7)))


# Przełącznik języka (Dodany ponownie)
lang_frame = tk.Frame(main_controls)
lang_frame.pack(side="right", padx=int(10 * max(1.0, scale_factor * 0.7)))

lang_label = tk.Label(lang_frame, text=get_text('LANGUAGE'))
lang_label.pack(side="left")

lang_var = tk.StringVar(value=get_text('LANG_PL'))

lang_combo_width = int(15 * max(1.0, scale_factor * 0.6))
lang_combo = ttk.Combobox(
    lang_frame,
    textvariable=lang_var,
    state="readonly",
    width=lang_combo_width
)
lang_combo['values'] = [get_text('LANG_PL'), get_text('LANG_EN')]
lang_combo.pack(side="left")

def language_changed(event):
    selected = lang_var.get()
    if selected == get_text('LANG_PL'):
        switch_language('pl')
    elif selected == get_text('LANG_EN'):
        switch_language('en')

lang_combo.bind('<<ComboboxSelected>>', language_changed)


# ===== Globalne / domyślne ustawienia dla nowych kontenerów =====
global_defaults_container = tk.Frame(root, pady=int(8 * max(1.0, scale_factor * 0.7)))
global_defaults_container.pack(fill="x")

# Górny rząd: etykiety + comboboxy
globals_top = tk.Frame(global_defaults_container)
globals_top.pack(fill="x")

g_combo_width = int(10 * max(1.0, scale_factor * 0.6))
g_method_combo_width = int(25 * max(1.0, scale_factor * 0.6))

global_color_label = tk.Label(globals_top, text=get_text('GLOBAL_COLOR_SPACE'))
global_color_label.pack(side="left", padx=int(8 * max(1.0, scale_factor * 0.7)))

global_color_space_var = tk.StringVar(value='RGB')
global_color_combo = ttk.Combobox(globals_top, state="readonly", width=g_combo_width,
                                  textvariable=global_color_space_var)
global_color_combo['values'] = ['RGB', 'HSV', 'LAB', 'CMYK']
global_color_combo.pack(side="left", padx=int(5 * max(1.0, scale_factor * 0.7)))

global_method_label = tk.Label(globals_top, text=get_text('GLOBAL_METHOD'))
global_method_label.pack(side="left", padx=int(15 * max(1.0, scale_factor * 0.7)))

global_method_var = tk.StringVar(value='Sobel')
global_method_combo = ttk.Combobox(globals_top, state="readonly", width=g_method_combo_width,
                                   textvariable=global_method_var)
global_method_combo['values'] = [
    'Sobel',
    'Sobel CV2',
    'Laplacian 4-neighbor',
    'Laplacian 8-neighbor',
    'Laplacian LoG',
    'Scharr',
    'Prewitt',
    'Canny',
    'Canny CV2',
    'Roberts'
]
global_method_combo.pack(side="left", padx=int(5 * max(1.0, scale_factor * 0.7)))

# Dolny rząd: przyciski Zastosuj do wszystkich
globals_buttons = tk.Frame(global_defaults_container)
globals_buttons.pack(fill="x", pady=int(5 * max(1.0, scale_factor * 0.7)))

def apply_global_color_to_all():
    val = global_color_space_var.get()
    for frame in comparison_frames:
        try:
            frame.color_space_combo.set(val)
        except Exception:
            pass

def apply_global_method_to_all():
    val = global_method_var.get()
    for frame in comparison_frames:
        try:
            frame.method_combo.set(val)
        except Exception:
            pass

apply_color_btn = tk.Button(globals_buttons, text=get_text('APPLY_COLOR_ALL'), command=apply_global_color_to_all)
apply_color_btn.pack(side="left", padx=int(8 * max(1.0, scale_factor * 0.7)))

apply_method_btn = tk.Button(globals_buttons, text=get_text('APPLY_METHOD_ALL'), command=apply_global_method_to_all)
apply_method_btn.pack(side="left", padx=int(8 * max(1.0, scale_factor * 0.7)))

# Podpowiedź: nowe ramki będą używać wybranych ustawień jako domyślne

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