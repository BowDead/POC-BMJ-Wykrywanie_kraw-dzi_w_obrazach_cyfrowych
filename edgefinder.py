import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "Python Launcher"

def refresh_file_list():
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and f != os.path.basename(__file__)]
    combo['values'] = py_files
    if py_files:
        combo.current(0)

def run_selected_file():
    filename = combo.get()
    if not filename:
        messagebox.showwarning("Brak wyboru", "Najpierw wybierz plik do uruchomienia!")
        return
    try:
        subprocess.Popen(["python", filename])
    except subprocess.CalledProcessError:
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas uruchamiania {filename}.")
    except Exception as e:
        messagebox.showerror("Błąd", str(e))


# GUI
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("400x150")
root.resizable(False, False)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(fill=tk.BOTH, expand=True)

label = tk.Label(frame, text="Wybierz plik Pythona do uruchomienia:")
label.pack(pady=(0, 10))

combo = ttk.Combobox(frame, state="readonly", width=40)
combo.pack(pady=(0, 10))

button_frame = tk.Frame(frame)
button_frame.pack()

refresh_button = tk.Button(button_frame, text="Odśwież listę", command=refresh_file_list)
refresh_button.grid(row=0, column=0, padx=5)

run_button = tk.Button(button_frame, text="Uruchom", command=run_selected_file)
run_button.grid(row=0, column=1, padx=5)

refresh_file_list()
root.mainloop()
