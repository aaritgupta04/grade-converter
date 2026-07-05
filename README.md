# Grade Converter

A Python desktop app for managing students and calculating Swiss school grades.
It uses Tkinter for the interface and saves data locally in JSON files.

## Features

- Create a local administrator account with an email and password
- Secure password hashing with PBKDF2
- Temporary lockout after repeated failed sign-in attempts
- Add and remove students
- Record scores for Maths, English, Sports, Drawing, and Science
- Calculate totals, averages, and Swiss grades from 1.0 to 6.0
- Save student and grade data automatically

## Grade calculation

Each subject accepts a score from 0 to 100. The app converts the average to a
Swiss grade in 0.5 steps:

- 0% becomes 1.0
- 60% becomes 4.0 (passing)
- 100% becomes 6.0

## Requirements

- Python 3
- Tkinter (included with most Python installations)

## Run the app

Clone the repository and enter its directory:

```bash
git clone https://github.com/aaritgupta04/grade-converter.git
cd grade-converter
```

Start the application:

```bash
python3 student.py
```

On the first run, create an account using a username, email, and password.
Future sign-ins use the email and password. No email verification is required.

## Local files

- `student.py` — main application
- `students.json` — saved students and grades
- `student.txt` — local account details and hashed password

The password itself is never stored. Keep `student.txt` private because it
contains account information.
