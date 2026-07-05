import os
import tkinter as tk
from datetime import datetime

ENTRY_FILE = "weather_log.txt"


def save_reading():
	temp = temp_entry.get().strip()
	if not temp:
		status_label.config(text="Enter temperature.", fg="red")
		return
	try:
		float(temp)
	except ValueError:
		status_label.config(text="Enter a valid number.", fg="red")
		return

	date = datetime.now().strftime("%Y-%m-%d")
	with open(ENTRY_FILE, "a", encoding="utf-8") as f:
		f.write(f"[{date}] {temp}\n")

	temp_entry.delete(0, tk.END)
	status_label.config(text="Saved ✓", fg="green")
	load_readings()


def load_readings():
	if not os.path.exists(ENTRY_FILE):
		open(ENTRY_FILE, "a", encoding="utf-8").close()

	listbox.delete(0, tk.END)
	with open(ENTRY_FILE, "r", encoding="utf-8") as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			if line.startswith("[") and "]" in line:
				date, content = line.split("]", 1)
				date = date[1:].strip()
				content = content.strip()
			else:
				date = "Unknown"
				content = line
			listbox.insert(tk.END, f"{date} - {content} °C")


root = tk.Tk()
root.title("Weather Log")
root.geometry("320x380")
root.resizable(False, False)
root.configure(padx=10, pady=10)

header = tk.Label(root, text="Daily Weather Log", font=("Arial", 14, "bold"))
header.pack(pady=(0, 8))

input_frame = tk.Frame(root)
input_frame.pack(pady=(0, 8))

temp_entry = tk.Entry(input_frame, width=12, font=("Arial", 12))
temp_entry.grid(row=0, column=0, padx=(0, 8))

save_btn = tk.Button(input_frame, text="Save", width=8, command=save_reading)
save_btn.grid(row=0, column=1)

status_label = tk.Label(root, text="", font=("Arial", 10))
status_label.pack(pady=(6, 8))

list_frame = tk.Frame(root)
list_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=40, height=12, font=("Arial", 11))
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

load_readings()
root.mainloop()

