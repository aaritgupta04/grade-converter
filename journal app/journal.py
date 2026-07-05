from datetime import datetime
#from turtle import write
def add_entry():
    entry = input("Write your journal entry: ")
    with open("journal.txt", "a") as file:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write("[{}] {}\n".format(date, entry))
    print("Entry saved!")

def view_entries():
    with open("journal.txt", "r") as file:
        print("\n--- Your Journal Entries ---")
        index = 0
        for line in file:
            print("{}: {}".format(index, line.strip()))
            index += 1

while True:
    print ("\n--- Journal App ---")
    print ("1. Add Entry")
    print ("2. View Entries") 
    print ("3. Exit")
    choice = input("Choose an option: ")
    if choice == "1":
        add_entry ()
    elif choice == "2":
        view_entries ()
    elif choice == "3":
        print ("Goodbye!")
        break 
    else:
        print("Please enter a valid option between 1-3")