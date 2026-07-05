import base64
import hashlib
import hmac
import json
import math
import re
import secrets
import tkinter as tk
import time
from json import JSONDecodeError
from pathlib import Path
from tkinter import messagebox, ttk



BG = "#F5F5F7"
CARD = "#FFFFFF"
TEXT = "#1D1D1F"
SECONDARY = "#6E6E73"
TERTIARY = "#AEAEB2"
ACCENT = "#007AFF"
ACCENT_HOVER = "#0068D9"
DIVIDER = "#D7D7DC"
FIELD = "#F2F2F7"
RED = "#D70015"
GREEN = "#248A3D"
SIDEBAR = "#ECECF0"

SUBJECTS = ("Maths", "English", "Sports", "Drawing", "Science")
DATA_FILE = Path(__file__).resolve().with_name("students.json")
AUTH_FILE = Path(__file__).resolve().with_name("student.txt")
PASSWORD_ITERATIONS = 600_000
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 30


def clean_name(value):
    """Return a consistently spaced student name."""
    return " ".join(value.split())


def normalize_email(value):
    """Validate and normalize an email address used for local sign-in."""
    email = value.strip().casefold()
    if (
        len(email) > 254
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    ):
        raise ValueError("Enter a valid email address.")
    return email


def calculate_result(scores):
    """Validate scores and return a Swiss school grade in 0.5 steps.

    The linear conversion maps 0% to 1.0 and 100% to 6.0, making 60% the
    minimum passing grade of 4.0.
    """
    if set(scores) != set(SUBJECTS):
        raise ValueError("A score is required for every subject.")

    try:
        numeric_scores = {subject: float(scores[subject]) for subject in SUBJECTS}
    except (TypeError, ValueError) as error:
        raise ValueError("Enter a number for every subject.") from error

    if any(
        not math.isfinite(score) or not 0 <= score <= 100
        for score in numeric_scores.values()
    ):
        raise ValueError("Each score must be between 0 and 100.")

    total = sum(numeric_scores.values())
    average = total / len(SUBJECTS)
    raw_grade = 1 + (5 * average / 100)
    grade = math.floor(raw_grade * 2 + 0.5) / 2
    return total, average, grade


def format_number(value):
    """Show whole numbers cleanly and retain one decimal when needed."""
    return f"{value:.1f}".rstrip("0").rstrip(".")


def format_grade(value):
    """Format a Swiss school grade, for example 4.0 or 5.5."""
    return f"{float(value):.1f}"


class AuthStore:
    """Create and verify one local account without storing its password."""

    @staticmethod
    def _read():
        try:
            data = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, JSONDecodeError):
            return {}

    @classmethod
    def has_account(cls):
        data = cls._read()
        required = {"username", "salt", "password_hash", "iterations"}
        return required.issubset(data)

    @classmethod
    def has_email(cls):
        data = cls._read()
        try:
            normalize_email(str(data["email"]))
        except (KeyError, TypeError, ValueError):
            return False
        return True

    @staticmethod
    def _derive_password(password, salt, iterations=PASSWORD_ITERATIONS):
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

    @classmethod
    def _validate_account_details(cls, username, email, password):
        username = clean_name(username)
        if not 3 <= len(username) <= 40:
            raise ValueError("Username must be 3–40 characters.")
        email = normalize_email(email)
        if not 8 <= len(password) <= 128:
            raise ValueError("Password must be 8–128 characters.")
        if password.isspace():
            raise ValueError("Choose a stronger password.")
        return username, email

    @staticmethod
    def _write(payload):
        temporary_file = AUTH_FILE.with_suffix(".tmp")
        try:
            temporary_file.write_text(
                json.dumps(payload, indent=2), encoding="utf-8"
            )
            temporary_file.replace(AUTH_FILE)
            try:
                AUTH_FILE.chmod(0o600)
            except OSError:
                pass
        except OSError as error:
            raise OSError("The account could not be saved.") from error

    @classmethod
    def create_account(cls, username, email, password):
        username, email = cls._validate_account_details(
            username, email, password
        )

        salt = secrets.token_bytes(16)
        password_hash = cls._derive_password(password, salt)
        payload = {
            "version": 2,
            "username": username,
            "email": email,
            "salt": base64.b64encode(salt).decode("ascii"),
            "password_hash": base64.b64encode(password_hash).decode("ascii"),
            "iterations": PASSWORD_ITERATIONS,
        }
        cls._write(payload)
        return username

    @classmethod
    def add_email(cls, email):
        """Upgrade an existing username-only account without changing its hash."""
        data = cls._read()
        if not cls.has_account():
            raise OSError("No existing account was found.")
        data["version"] = 2
        data["email"] = normalize_email(email)
        data.pop("email_verified", None)
        cls._write(data)

    @classmethod
    
    def verify(cls, identifier, password):
        data = cls._read()
        try:
            saved_username = str(data["username"])
            salt = base64.b64decode(data["salt"], validate=True)
            expected_hash = base64.b64decode(
                data["password_hash"], validate=True
            )
            iterations = int(data["iterations"])
            if not 100_000 <= iterations <= 2_000_000:
                return False
        except (KeyError, TypeError, ValueError):
            return False

        candidate_hash = cls._derive_password(password[:128], salt, iterations)
        saved_identifier = (
            str(data.get("email"))
            if cls.has_email()
            else saved_username
        )
        identifier_matches = hmac.compare_digest(
            identifier.strip().casefold().encode("utf-8"),
            saved_identifier.strip().casefold().encode("utf-8"),
        )
        password_matches = hmac.compare_digest(candidate_hash, expected_hash)
        return identifier_matches and password_matches

    @classmethod
   
   
    def username(cls):
        return str(cls._read().get("username", ""))

    @classmethod
    def email(cls):
        return str(cls._read().get("email", ""))



class RoundedButton(tk.Canvas):
    """A small canvas button so the interface stays consistent on every OS."""


    def __init__(
        self, parent, text, command, width=130, primary=True, danger=False
    ):
        super().__init__(
            parent,
            width=width,
            height=42,
            bg=parent.cget("bg"),
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.command = command
        self.primary = primary

        if danger:
            self.normal, self.hover, foreground = "#FFF0F1", "#FFE3E6", RED
        elif primary:
            self.normal, self.hover, foreground = ACCENT, ACCENT_HOVER, CARD
        else:
            self.normal, self.hover, foreground = FIELD, "#E8E8ED", TEXT

        self.shape = self.create_polygon(
            self._rounded_points(1, 1, width - 1, 41, 13),
            smooth=True,
            splinesteps=24,
            fill=self.normal,
            outline=self.normal,
        )
        self.create_text(
            width / 2,
            21,
            text=text,
            fill=foreground,
            font=("SF Pro Text", 11, "bold"),
        )
        self.bind("<Enter>", lambda _event: self.itemconfigure(self.shape, fill=self.hover))
        self.bind("<Leave>", lambda _event: self.itemconfigure(self.shape, fill=self.normal))
        self.bind("<Button-1>", lambda _event: self.command())

    @staticmethod
    
    def _rounded_points(x1, y1, x2, y2, radius):
        return [
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]




class LoginView:
    """First-run account setup and returning-user sign-in screen."""

    def __init__(self, root, on_authenticated):
        self.root = root
        self.on_authenticated = on_authenticated
        self.is_setup = not AuthStore.has_account()
        self.needs_email_upgrade = (
            AuthStore.has_account() and not AuthStore.has_email()
        )
        self.failed_attempts = 0
        self.locked_until = 0
        self.lockout_timer = None
        self.show_password = tk.BooleanVar(value=False)
        self._build()

    def _build(self):
        if self.is_setup:
            title = "Student Manager — Account Setup"
            geometry = "560x735"
        elif self.needs_email_upgrade:
            title = "Student Manager — Add Email"
            geometry = "560x690"
        else:
            title = "Student Manager — Sign In"
            geometry = "560x590"
        self.root.title(title)
        self.root.geometry(geometry)
        self.root.minsize(520, 560)
        self.root.configure(bg=BG)

        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(self.container, bg=CARD, padx=42, pady=36)
        card.place(relx=0.5, rely=0.5, anchor="center", width=440)

        tk.Label(
            card,
            text="●",
            bg=CARD,
            fg=ACCENT,
            font=("SF Pro Display", 25),
        ).pack()
        tk.Label(
            card,
            text=(
                "Create your account"
                if self.is_setup
                else "Add your email"
                if self.needs_email_upgrade
                else "Welcome back"
            ),
            bg=CARD,
            fg=TEXT,
            font=("SF Pro Display", 24, "bold"),
        ).pack(pady=(8, 5))
        tk.Label(
            card,
            text=(
                "Set up your administrator login."
                if self.is_setup
                else "Confirm your old login and add your email."
                if self.needs_email_upgrade
                else "Sign in to open your classroom."
            ),
            bg=CARD,
            fg=SECONDARY,
            font=("SF Pro Text", 11),
        ).pack(pady=(0, 25))

        self.username_entry = None
        if self.is_setup or self.needs_email_upgrade:
            self.username_entry = self._field(card, "Username")
        if self.needs_email_upgrade:
            self.username_entry.insert(0, AuthStore.username())

        self.email_entry = self._field(card, "Email")
        if not self.is_setup and not self.needs_email_upgrade:
            self.email_entry.insert(0, AuthStore.email())

        self.password_entry = self._field(card, "Password", secret=True)
        self.confirm_entry = None
        if self.is_setup:
            self.confirm_entry = self._field(card, "Confirm password", secret=True)

        show = tk.Checkbutton(
            card,
            text="Show password",
            variable=self.show_password,
            command=self._toggle_password,
            bg=CARD,
            activebackground=CARD,
            fg=SECONDARY,
            selectcolor=CARD,
            highlightthickness=0,
            bd=0,
            font=("SF Pro Text", 10),
        )
        show.pack(anchor="w", pady=(2, 4))

        self.error_label = tk.Label(
            card,
            text="",
            bg=CARD,
            fg=RED,
            font=("SF Pro Text", 10),
            wraplength=340,
        )
        self.error_label.pack(pady=(3, 8))

        button_text = (
            "Create account"
            if self.is_setup
            else "Add email"
            if self.needs_email_upgrade
            else "Sign in"
        )
        RoundedButton(card, button_text, self.submit, width=180).pack()

        self.root.bind("<Return>", lambda _event: self.submit())
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        target = self.username_entry if self.is_setup else self.password_entry
        target.focus_set()

    @staticmethod
    def _field(parent, label, secret=False):
        tk.Label(
            parent,
            text=label,
            bg=CARD,
            fg=SECONDARY,
            font=("SF Pro Text", 9, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 6))
        entry = tk.Entry(
            parent,
            bg=FIELD,
            fg=TEXT,
            insertbackground=ACCENT,
            relief=tk.FLAT,
            bd=0,
            show="●" if secret else "",
            font=("SF Pro Text", 12),
        )
        entry.pack(fill=tk.X, ipady=10, pady=(0, 15))
        return entry

    def _toggle_password(self):
        mask = "" if self.show_password.get() else "●"
        self.password_entry.config(show=mask)
        if self.confirm_entry:
            self.confirm_entry.config(show=mask)

    def submit(self):
        if time.monotonic() < self.locked_until:
            return

        username = (
            clean_name(self.username_entry.get()) if self.username_entry else ""
        )
        email = self.email_entry.get()
        password = self.password_entry.get()
        if self.is_setup:
            if password != self.confirm_entry.get():
                self._show_error("Passwords do not match.")
                return
            try:
                username = AuthStore.create_account(
                    username, email, password
                )
            except (ValueError, OSError) as error:
                self._show_error(str(error))
                return
            self._finish(username)
            return

        identifier = username if self.needs_email_upgrade else email
        if len(identifier) > 254 or len(password) > 128:
            valid_login = False
        else:
            valid_login = AuthStore.verify(identifier, password)
        if valid_login:
            if self.needs_email_upgrade:
                try:
                    email = normalize_email(email)
                except ValueError as error:
                    self._show_error(str(error))
                    return
                try:
                    AuthStore.add_email(email)
                except (ValueError, OSError) as error:
                    self._show_error(str(error))
                    return
                self._finish(AuthStore.username())
            else:
                self._finish(AuthStore.username())
            return

        self.failed_attempts += 1
        remaining = MAX_LOGIN_ATTEMPTS - self.failed_attempts
        self.password_entry.delete(0, tk.END)
        self.password_entry.focus_set()
        if remaining <= 0:
            self.failed_attempts = 0
            self.locked_until = time.monotonic() + LOCKOUT_SECONDS
            self._update_lockout()
        else:
            self._show_error(
                f"Incorrect {'username' if self.needs_email_upgrade else 'email'} "
                f"or password. {remaining} attempt"
                f"{'s' if remaining != 1 else ''} remaining."
            )

    def _update_lockout(self):
        remaining = max(0, math.ceil(self.locked_until - time.monotonic()))
        if remaining:
            self._show_error(f"Too many attempts. Try again in {remaining} seconds.")
            self.lockout_timer = self.root.after(1000, self._update_lockout)
        else:
            self.lockout_timer = None
            self._show_error("You can try signing in again.", SECONDARY)

    def _show_error(self, message, color=RED):
        self.error_label.config(text=message, fg=color)


    def _finish(self, username):
        if self.lockout_timer is not None:
            self.root.after_cancel(self.lockout_timer)
        self.root.unbind("<Return>")
        self.root.unbind("<Escape>")
        self.container.destroy()
        self.on_authenticated(username)




class StudentManager:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.students = []
        self.grades = {}
        self.status_timer = None
        self._configure_window()
        self._configure_styles()
        self._build_interface()
        self.load_data()

    def _configure_window(self):
        self.root.title("Students")
        self.root.geometry("960x620")
        self.root.minsize(820, 560)
        self.root.configure(bg=BG)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        try:
            self.root.tk.call(
                "tk::unsupported::MacWindowStyle",
                "style",
                self.root._w,
                "document",
                "closeBox",
            )
        except tk.TclError:
            pass

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Student.Treeview",
            background=CARD,
            fieldbackground=CARD,
            foreground=TEXT,
            borderwidth=0,
            rowheight=48,
            font=("SF Pro Text", 11),
        )
        style.map(
            "Student.Treeview",
            background=[("selected", "#E3F0FF")],
            foreground=[("selected", TEXT)],
        )
        style.configure(
            "Student.Treeview.Heading",
            background=CARD,
            foreground=SECONDARY,
            relief="flat",
            borderwidth=0,
            font=("SF Pro Text", 9, "bold"),
        )

    def _build_interface(self):
        self._build_sidebar()
        self._build_main_panel()

    def _build_sidebar(self):
        sidebar = tk.Frame(self.root, bg=SIDEBAR, width=245)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        tk.Label(
            sidebar,
            text="Classroom",
            bg=SIDEBAR,
            fg=TEXT,
            font=("SF Pro Display", 24, "bold"),
            anchor="w",
        ).pack(fill=tk.X, padx=24, pady=(34, 4))

        tk.Label(
            sidebar,
            text="STUDENT MANAGER",
            bg=SIDEBAR,
            fg=SECONDARY,
            font=("SF Pro Text", 9, "bold"),
            anchor="w",
        ).pack(fill=tk.X, padx=25, pady=(18, 8))

        active = tk.Frame(sidebar, bg=CARD, padx=13, pady=12)
        active.pack(fill=tk.X, padx=14)
        tk.Label(
            active,
            text="●",
            bg=CARD,
            fg=ACCENT,
            font=("SF Pro Text", 9),
        ).pack(side=tk.LEFT, padx=(0, 9))
        tk.Label(
            active,
            text="All Students",
            bg=CARD,
            fg=TEXT,
            font=("SF Pro Text", 11, "bold"),
        ).pack(side=tk.LEFT)

        summary = tk.Frame(sidebar, bg=SIDEBAR)
        summary.pack(side=tk.BOTTOM, fill=tk.X, padx=24, pady=28)
        self.total_label = tk.Label(
            summary,
            text="0",
            bg=SIDEBAR,
            fg=TEXT,
            font=("SF Pro Display", 30, "bold"),
            anchor="w",
        )
        self.total_label.pack(fill=tk.X)
        tk.Label(
            summary,
            text="students in this class",
            bg=SIDEBAR,
            fg=SECONDARY,
            font=("SF Pro Text", 10),
            anchor="w",
        ).pack(fill=tk.X)

        account = tk.Frame(sidebar, bg=SIDEBAR)
        account.pack(side=tk.BOTTOM, fill=tk.X, padx=24, pady=(0, 6))
        tk.Label(
            account,
            text="SIGNED IN AS",
            bg=SIDEBAR,
            fg=TERTIARY,
            font=("SF Pro Text", 8, "bold"),
            anchor="w",
        ).pack(fill=tk.X)
        tk.Label(
            account,
            text=self.username,
            bg=SIDEBAR,
            fg=TEXT,
            font=("SF Pro Text", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(3, 0))

    def _build_main_panel(self):
        main = tk.Frame(self.root, bg=BG)
        main.grid(row=0, column=1, sticky="nsew", padx=38, pady=31)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)

        header = tk.Frame(main, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 22))
        header.grid_columnconfigure(0, weight=1)
        tk.Label(
            header,
            text="Students",
            bg=BG,
            fg=TEXT,
            font=("SF Pro Display", 27, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        self.status_label = tk.Label(
            header,
            text="",
            bg=BG,
            fg=GREEN,
            font=("SF Pro Text", 10),
        )
        self.status_label.grid(row=0, column=1, sticky="e")

        add_card = tk.Frame(main, bg=CARD, padx=20, pady=18)
        add_card.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        add_card.grid_columnconfigure(0, weight=1)
        tk.Label(
            add_card,
            text="Add someone new",
            bg=CARD,
            fg=TEXT,
            font=("SF Pro Text", 13, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 11))

        self.name_entry = tk.Entry(
            add_card,
            bg=FIELD,
            fg=TEXT,
            insertbackground=ACCENT,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=FIELD,
            highlightcolor=ACCENT,
            font=("SF Pro Text", 12),
        )
        self.name_entry.grid(row=1, column=0, sticky="ew", ipady=11, padx=(0, 12))
        self.name_entry.bind("<Return>", lambda _event: self.add_student())
        RoundedButton(add_card, "Add student", self.add_student, width=126).grid(
            row=1, column=1
        )

        list_card = tk.Frame(main, bg=CARD, padx=20, pady=16)
        list_card.grid(row=2, column=0, sticky="nsew")
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)

        list_header = tk.Frame(list_card, bg=CARD)
        list_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        list_header.grid_columnconfigure(0, weight=1)
        tk.Label(
            list_header,
            text="Class list",
            bg=CARD,
            fg=TEXT,
            font=("SF Pro Text", 13, "bold"),
        ).grid(row=0, column=0, sticky="w")
        self.hint_label = tk.Label(
            list_header,
            text="Select a student to manage grades",
            bg=CARD,
            fg=TERTIARY,
            font=("SF Pro Text", 9),
        )
        self.hint_label.grid(row=0, column=1, sticky="e")

        self.student_list = ttk.Treeview(
            list_card,
            columns=("student", "grade"),
            show="headings",
            selectmode="browse",
            style="Student.Treeview",
        )
        self.student_list.heading("student", text="STUDENT")
        self.student_list.heading("grade", text="SWISS GRADE")
        self.student_list.column("student", minwidth=220, width=380, anchor="w")
        self.student_list.column("grade", minwidth=110, width=140, anchor="center")
        self.student_list.grid(row=1, column=0, sticky="nsew")
        self.student_list.bind("<Double-1>", lambda _event: self.open_grade_calculator())
        self.student_list.bind("<Delete>", lambda _event: self.remove_student())

        scrollbar = ttk.Scrollbar(
            list_card, orient=tk.VERTICAL, command=self.student_list.yview
        )
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.student_list.configure(yscrollcommand=scrollbar.set)

        actions = tk.Frame(list_card, bg=CARD)
        actions.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        actions.grid_columnconfigure(0, weight=1)
        RoundedButton(
            actions,
            "Remove",
            self.remove_student,
            width=96,
            primary=False,
            danger=True,
        ).grid(row=0, column=1, padx=(8, 0))
        RoundedButton(
            actions,
            "Calculate grades",
            self.open_grade_calculator,
            width=154,
        ).grid(row=0, column=2, padx=(8, 0))

        self.name_entry.focus_set()
        self.root.bind("<Command-g>", lambda _event: self.open_grade_calculator())
        self.root.bind("<Control-g>", lambda _event: self.open_grade_calculator())

    def set_status(self, text, color=GREEN):
        if self.status_timer is not None:
            self.root.after_cancel(self.status_timer)
        self.status_label.config(text=text, fg=color)
        self.status_timer = self.root.after(3000, self.clear_status)

    def clear_status(self):
        self.status_label.config(text="")
        self.status_timer = None

    def load_data(self):
        """Load saved records, ignoring malformed individual entries."""
        if not DATA_FILE.exists():
            self.refresh_student_list()
            return

        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            raw_students = data.get("students", [])
            raw_grades = data.get("grades", {})
            if not isinstance(raw_students, list) or not isinstance(raw_grades, dict):
                raise ValueError("Unexpected data structure")

            seen = set()
            for value in raw_students:
                if not isinstance(value, str):
                    continue
                name = clean_name(value)
                key = name.casefold()
                if name and key not in seen:
                    self.students.append(name)
                    seen.add(key)

            # Recalculate results from their scores. This also migrates records
            # created by older versions that stored letter grades.
            for name in self.students:
                result = raw_grades.get(name)
                if not isinstance(result, dict) or not isinstance(
                    result.get("scores"), dict
                ):
                    continue
                try:
                    total, average, grade = calculate_result(result["scores"])
                except (TypeError, ValueError):
                    continue
                self.grades[name] = {
                    "scores": {
                        subject: float(result["scores"][subject])
                        for subject in SUBJECTS
                    },
                    "total": total,
                    "average": average,
                    "grade": grade,
                }
            self.refresh_student_list()
        except (OSError, JSONDecodeError, ValueError, TypeError):
            self.students = []
            self.grades = {}
            self.refresh_student_list()
            self.set_status("Saved data could not be read", RED)

    def save_data(self):
        """Save atomically so an interrupted write cannot corrupt the records."""
        payload = {"version": 1, "students": self.students, "grades": self.grades}
        temporary_file = DATA_FILE.with_suffix(".tmp")
        try:
            temporary_file.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            temporary_file.replace(DATA_FILE)
            return True
        except OSError:
            self.set_status("Changes could not be saved", RED)
            return False

    def refresh_student_list(self, selected_name=None):
        self.student_list.delete(*self.student_list.get_children())
        selected_item = None
        for name in self.students:
            result = self.grades.get(name)
            if result:
                grade = float(result.get("grade", 1))
                outcome = "Passed" if grade >= 4 else "Not passed"
                result_text = f"{format_grade(grade)} · {outcome}"
            else:
                result_text = "Not graded"
            item_id = self.student_list.insert(
                "", tk.END, values=(name, result_text)
            )
            if name == selected_name:
                selected_item = item_id

        self.total_label.config(text=str(len(self.students)))
        if selected_item:
            self.student_list.selection_set(selected_item)
            self.student_list.focus(selected_item)
            self.student_list.see(selected_item)

    def add_student(self):
        name = clean_name(self.name_entry.get())
        if not name:
            self.set_status("Enter a student name", RED)
            self.name_entry.focus_set()
            return

        if name.casefold() in {student.casefold() for student in self.students}:
            self.set_status("That student is already here", RED)
            return

        self.students.append(name)
        self.save_data()
        self.refresh_student_list(selected_name=name)
        self.name_entry.delete(0, tk.END)
        self.set_status(f"Added {name}")
        self.name_entry.focus_set()

    def selected_student(self):
        selected = self.student_list.selection()
        if not selected:
            return None, None
        item_id = selected[0]
        return item_id, self.student_list.item(item_id, "values")[0]

    def remove_student(self):
        item_id, name = self.selected_student()
        if not item_id:
            self.set_status("Select a student first", RED)
            return

        confirmed = messagebox.askyesno(
            "Remove Student",
            f"Remove {name} and their saved grades?",
            parent=self.root,
        )
        if not confirmed:
            return

        self.students.remove(name)
        self.grades.pop(name, None)
        self.save_data()
        self.refresh_student_list()
        self.set_status(f"Removed {name}", SECONDARY)

   
   
   
   
    
    
    def open_grade_calculator(self):
        item_id, student_name = self.selected_student()
        if not item_id:
            self.set_status("Select a student first", RED)
            return

        window = tk.Toplevel(self.root)
        window.title("Grade Calculator")
        window.geometry("500x590")
        window.resizable(False, False)
        window.configure(bg=BG)
        window.transient(self.root)
        window.grab_set()

        tk.Label(
            window,
            text="Grade Calculator",
            bg=BG,
            fg=TEXT,
            font=("SF Pro Display", 24, "bold"),
            anchor="w",
        ).pack(fill=tk.X, padx=34, pady=(30, 3))
        tk.Label(
            window,
            text=f"Enter scores for {student_name}",
            bg=BG,
            fg=SECONDARY,
            font=("SF Pro Text", 11),
            anchor="w",
        ).pack(fill=tk.X, padx=35, pady=(0, 20))

        form = tk.Frame(window, bg=CARD, padx=24, pady=18)
        form.pack(fill=tk.X, padx=32)
        form.grid_columnconfigure(1, weight=1)
        entries = {}

        previous = self.grades.get(student_name, {}).get("scores", {})
        for row, subject in enumerate(SUBJECTS):
            tk.Label(
                form,
                text=subject,
                bg=CARD,
                fg=TEXT,
                font=("SF Pro Text", 11),
                anchor="w",
            ).grid(row=row, column=0, sticky="w", pady=8)
            entry = tk.Entry(
                form,
                bg=FIELD,
                fg=TEXT,
                insertbackground=ACCENT,
                relief=tk.FLAT,
                bd=0,
                justify="center",
                font=("SF Pro Text", 11),
                width=9,
            )
            entry.grid(row=row, column=1, sticky="e", ipady=7, pady=5)
            if subject in previous:
                entry.insert(0, str(previous[subject]))
            entries[subject] = entry

        error_label = tk.Label(
            window,
            text="0–100 points · Swiss grades 1.0–6.0 · 4.0 passes",
            bg=BG,
            fg=SECONDARY,
            font=("SF Pro Text", 10),
        )
        error_label.pack(pady=(15, 8))

       
       
       
       
        def calculate():
            try:
                scores = {subject: entries[subject].get() for subject in SUBJECTS}
                total, average, grade = calculate_result(scores)
            except (ValueError, TypeError) as error:
                message = str(error) or "Enter a number for every subject."
                error_label.config(text=message, fg=RED)
                return

            self.grades[student_name] = {
                "scores": {subject: float(scores[subject]) for subject in SUBJECTS},
                "total": total,
                "average": average,
                "grade": grade,
            }
            self.save_data()
            self.refresh_student_list(selected_name=student_name)
            self.show_result(window, student_name, total, average, grade)

        RoundedButton(window, "Calculate", calculate, width=150).pack(pady=(5, 25))
        window.bind("<Return>", lambda _event: calculate())
        window.bind("<Escape>", lambda _event: window.destroy())
        entries[SUBJECTS[0]].focus_set()

   
   
    def show_result(self, grade_window, student_name, total, average, grade):
        grade_window.destroy()
        result = tk.Toplevel(self.root)
        result.title("Grade Result")
        result.geometry("430x390")
        result.resizable(False, False)
        result.configure(bg=BG)
        result.transient(self.root)
        result.grab_set()

        passed = grade >= 4
        grade_color = GREEN if passed else RED
        tk.Label(
            result,
            text="Result",
            bg=BG,
            fg=SECONDARY,
            font=("SF Pro Text", 10, "bold"),
        ).pack(pady=(36, 8))
        tk.Label(
            result,
            text=format_grade(grade),
            bg=BG,
            fg=grade_color,
            font=("SF Pro Display", 52, "bold"),
        ).pack()
        tk.Label(
            result,
            text="Passed" if passed else "Not passed",
            bg=BG,
            fg=grade_color,
            font=("SF Pro Text", 11, "bold"),
        ).pack(pady=(0, 4))
        tk.Label(
            result,
            text=student_name,
            bg=BG,
            fg=TEXT,
            font=("SF Pro Text", 15, "bold"),
        ).pack(pady=(2, 18))

        stats = tk.Frame(result, bg=CARD, padx=24, pady=18)
        stats.pack(fill=tk.X, padx=34)
        for column, (label, value) in enumerate(
            (
                ("TOTAL", f"{format_number(total)} / 500"),
                ("AVERAGE", f"{format_number(average)}%"),
            )
        ):
            block = tk.Frame(stats, bg=CARD)
            block.grid(row=0, column=column, padx=24)
            tk.Label(
                block,
                text=label,
                bg=CARD,
                fg=SECONDARY,
                font=("SF Pro Text", 9, "bold"),
            ).pack()
            tk.Label(
                block,
                text=value,
                bg=CARD,
                fg=TEXT,
                font=("SF Pro Text", 15, "bold"),
            ).pack(pady=(4, 0))

        RoundedButton(result, "Done", result.destroy, width=120).pack(pady=25)
        result.bind("<Return>", lambda _event: result.destroy())
        result.bind("<Escape>", lambda _event: result.destroy())
        self.set_status(f"Grades updated for {student_name}")

def main():
    root = tk.Tk()
    LoginView(root, lambda username: StudentManager(root, username))
    root.mainloop()

if __name__ == "__main__":
    main()
