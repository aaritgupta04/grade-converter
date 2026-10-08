import tkinter as tk
from tkinter import messagebox


def calculate():
    try:
        people = int(people_entry.get())
        price = float(price_entry.get())

        if people <= 0:
            raise ValueError("Number of people must be greater than zero.")

        total = people * price

        result_label.config(
            text=f"Total Price: CHF {total:.2f}"
        )

    except ValueError:
        messagebox.showerror(
            "Error",
            "Please enter valid numbers."
        )


def add_purchase():
    name = name_entry.get()
    item = item_entry.get()

    if name == "" or item == "":
        messagebox.showerror(
            "Error",
            "Please enter a name and an item."
        )
    else:
        purchase_list.insert(
            tk.END,
            name + " bought: " + item + "\n")

        name_entry.delete(0, tk.END)
        item_entry.delete(0, tk.END)


window = tk.Tk()
window.title("Movie Ticket Calculator")
window.geometry("400x500")

tk.Label(
    window,
    text="Movie Ticket Calculator",
    font=("Arial", 18, "bold")
).pack(pady=15)

tk.Label(window, text="Number of people:").pack()
people_entry = tk.Entry(window)
people_entry.pack(pady=5)

tk.Label(window, text="Ticket price per person:").pack()
price_entry = tk.Entry(window)
price_entry.pack(pady=5)

tk.Button(
    window,
    text="Calculate",
    command=calculate
).pack(pady=10)

result_label = tk.Label(
    window,
    text="Total Price: CHF 0.00",
    font=("Arial", 14, "bold")
)
result_label.pack(pady=10)

tk.Label(
    window,
    text="What People Bought",
    font=("Arial", 14, "bold")
).pack(pady=10)

tk.Label(window, text="Person's name:").pack()
name_entry = tk.Entry(window)
name_entry.pack(pady=5)

tk.Label(window, text="What did they buy?").pack()
item_entry = tk.Entry(window)
item_entry.pack(pady=5)

tk.Button(
    window,
    text="Add Purchase",
    command=add_purchase
).pack(pady=10)

purchase_list = tk.Text(window, width=40, height=6)
purchase_list.pack()

window.mainloop()