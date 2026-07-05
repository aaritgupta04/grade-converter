import os
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

ENTRY_FILE = "journal.txt"


def save_entry():
    entry = text_input.get("1.0", tk.END).strip()
    if not entry:
        status_label.config(text="⚠️ Please write something before saving.", fg="red")
        return

    with open(ENTRY_FILE, "a", encoding="utf-8") as file:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{date}] {entry}\n")

    text_input.delete("1.0", tk.END)
    status_label.config(text="✓ Entry saved!", fg="green")
    load_entries()


def load_entries():
    if not os.path.exists(ENTRY_FILE):
        open(ENTRY_FILE, "a", encoding="utf-8").close()

    display_text.config(state=tk.NORMAL)
    display_text.delete("1.0", tk.END)

    with open(ENTRY_FILE, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    if not lines:
        display_text.insert("1.0", "No entries yet. Write your first journal entry!")
    else:
        for line in lines:
            if line.startswith("[") and "]" in line:
                date, content = line.split("]", 1)
                date = date[1:].strip()
                content = content.strip()
            else:
                date = "Unknown date"
                content = line

            display_text.insert(tk.END, f"{date}\n", "date")
            display_text.insert(tk.END, f"{content}\n\n", "entry")

    display_text.config(state=tk.DISABLED)


root = tk.Tk()
root.title("Journal App")
root.geometry("500x520")
root.resizable(False, False)
root.configure(padx=16, pady=16)

header = tk.Label(root, text="My Journal", font=("Arial", 18, "bold"))
header.pack(pady=(0, 10))

instruction = tk.Label(root, text="Write a new entry below, then save it.", font=("Arial", 10))
instruction.pack(pady=(0, 10))

text_input = tk.Text(root, height=6, width=55, wrap=tk.WORD, font=("Arial", 11))
text_input.pack(pady=(0, 10))

button_frame = tk.Frame(root)
button_frame.pack(pady=(0, 8))

save_button = tk.Button(button_frame, text="Save Entry", width=14, command=save_entry)
save_button.grid(row=0, column=0, padx=6)

refresh_button = tk.Button(button_frame, text="Refresh Entries", width=14, command=load_entries)
refresh_button.grid(row=0, column=1, padx=6)

status_label = tk.Label(root, text="", font=("Arial", 10))
status_label.pack(pady=(0, 10))

separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
separator.pack(fill=tk.X, pady=6)

entries_label = tk.Label(root, text="Your Entries", font=("Arial", 14, "bold"))
entries_label.pack(pady=(0, 6))

display_text = scrolledtext.ScrolledText(root, height=14, width=58, wrap=tk.WORD, font=("Arial", 11))
display_text.pack()
display_text.tag_configure("date", foreground="#2A4D8F", font=("Arial", 10, "bold"))
display_text.tag_configure("entry", foreground="#333333", font=("Arial", 11))

load_entries()
root.mainloop()
