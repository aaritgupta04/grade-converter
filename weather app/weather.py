from datetime import datetime

LOG_FILE = "weather_log.txt"


def add_reading():
	date = datetime.now().strftime("%Y-%m-%d")
	temp = input("Enter today's temperature (°C): ")
	try:
		# allow floats
		float(temp)
	except ValueError:
		print("Please enter a valid number for temperature.")
		return

	with open(LOG_FILE, "a", encoding="utf-8") as f:
		f.write(f"[{date}] {temp}\n")

	print("Reading saved!")


def view_readings():
	try:
		with open(LOG_FILE, "r", encoding="utf-8") as f:
			lines = [line.strip() for line in f if line.strip()]
	except FileNotFoundError:
		print("No readings yet. Add your first temperature reading!")
		return

	if not lines:
		print("No readings yet. Add your first temperature reading!")
		return

	print("\n--- Daily Weather Log ---")
	for idx, line in enumerate(lines):
		print(f"{idx}: {line}")


def main():
	while True:
		print("\n--- Weather Logger ---")
		print("1. Add Today's Temperature")
		print("2. View Readings")
		print("3. Exit")
		choice = input("Choose an option: ")
		if choice == "1":
			add_reading()
		elif choice == "2":
			view_readings()
		elif choice == "3":
			print("Goodbye!")
			break
		else:
			print("Please enter a valid option between 1-3")


if __name__ == "__main__":
	main()

