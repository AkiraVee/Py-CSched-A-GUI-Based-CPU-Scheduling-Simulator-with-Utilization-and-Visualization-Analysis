"""
============================================================
GENERAL NOTE (NEW):
This file integrates a Tkinter-based GUI on top of the
existing CLI login system. All database, hashing, and
authorization logic remains unchanged. Tkinter is used
only as a presentation layer to provide cross-platform,
masked password input and visual navigation.
============================================================
"""

import sqlite3
import hashlib
import os
import tkinter as tk
from tkinter import messagebox, ttk

# NOTE:
# The database file was being created in unexpected directories because of two issues:
#
# 1) The database path must be anchored to this script’s location, not the current
#    working directory. Using os.path.abspath(__file__) ensures SQLite always uses
#    the same users.db file regardless of how the program is run.
#
# 2) Defining DATABASE_FILE = "users.db" again later in the file overwrote the correct
#    absolute path and caused SQLite to silently create a new database elsewhere.
#    There must be ONLY ONE definition of DATABASE_FILE.
#
# Correct usage:
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATABASE_FILE = os.path.join(BASE_DIR, "users.db")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "users.db")

# >>> ADD FOR ADMIN <<<
# Reserved administrator username
ADMIN_USERNAME = "admin"

# =========================
# >>> UI ADDITION <<<
# Consistent CLI section header display (CLI ONLY)
# =========================
def display_header(title):
    print("\n==============================")
    print(f"{title:^30}")
    print("==============================")

# =========================
# SECURITY: PASSWORD HASHING
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# INITIALIZE DATABASE
# =========================
def initialize_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            security_question TEXT NOT NULL,
            security_answer TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    conn.close()

# >>> ADD FOR ADMIN <<<
# Schema migration safety
def add_role_column_if_missing():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [c[1] for c in cursor.fetchall()]
    if "role" not in columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'"
        )
        conn.commit()
    conn.close()

# >>> ADD FOR ADMIN <<<
# Default admin bootstrap
def create_default_admin():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username FROM users WHERE username = ?",
        (ADMIN_USERNAME,)
    )
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (
                username, password,
                security_question, security_answer, role
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            ADMIN_USERNAME,
            hash_password("admin123"),
            "Default admin question",
            "admin",
            "admin"
        ))
        conn.commit()
    conn.close()

# ============================================================
# TKINTER GUI CLASS
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("System Login")
        self.root.geometry("460x540")
        self.root.resizable(False, False)

        self.container = tk.Frame(root, padx=20, pady=20)
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()

    def clear_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ---------------- LOGIN ----------------
    def show_login_screen(self):
        self.clear_screen()

        tk.Label(self.container, text="LOGIN", font=("Arial", 18, "bold")).pack(pady=15)

        form = tk.Frame(self.container)
        form.pack(pady=10)

        tk.Label(form, text="Username").grid(row=0, column=0, sticky="w")
        self.u_entry = tk.Entry(form, width=25)
        self.u_entry.grid(row=0, column=1, pady=5)

        tk.Label(form, text="Password").grid(row=1, column=0, sticky="w")
        self.p_entry = tk.Entry(form, show="*", width=25)
        self.p_entry.grid(row=1, column=1, pady=5)

        tk.Button(self.container, text="Login", width=20, command=self.handle_login).pack(pady=8)
        tk.Button(self.container, text="Sign Up", width=20, command=self.show_signup_screen).pack(pady=4)
        tk.Button(self.container, text="Forgot Password?", command=self.show_forgot_screen,
                  fg="blue", relief="flat").pack(pady=6)
        
        # >>> NEW: EXIT BUTTON <<<
        tk.Button(
            self.container,
            text="Exit",
            width=20,
            fg="red",
            command=self.exit_program
        ).pack(pady=8)

    def handle_login(self):
        username = self.u_entry.get()
        password = self.p_entry.get()

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password, role FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == hash_password(password):
            if result[1] == "admin":
                self.show_admin_menu()
            else:
                messagebox.showinfo("Login Success", "Welcome User!")
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    # ---------------- SIGN UP ----------------
    def show_signup_screen(self):
        self.clear_screen()

        tk.Label(self.container, text="SIGN UP", font=("Arial", 18, "bold")).pack(pady=15)

        form = tk.Frame(self.container)
        form.pack(pady=10)

        labels = ["Username", "Password", "Security Question", "Answer"]
        self.signup_entries = {}

        for i, label in enumerate(labels):
            tk.Label(form, text=label).grid(row=i, column=0, sticky="w")
            entry = tk.Entry(form, show="*" if label == "Password" else "", width=25)
            entry.grid(row=i, column=1, pady=5)
            self.signup_entries[label] = entry

        tk.Button(self.container, text="Register", width=20, command=self.handle_signup).pack(pady=10)
        tk.Button(self.container, text="Back", command=self.show_login_screen).pack()

    def handle_signup(self):
        u = self.signup_entries["Username"].get()
        p = self.signup_entries["Password"].get()
        q = self.signup_entries["Security Question"].get()
        a = self.signup_entries["Answer"].get()

        if u.lower() == ADMIN_USERNAME:
            messagebox.showwarning("Error", "This username is reserved.")
            return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                (u, hash_password(p), q, a, "user")
            )
            conn.commit()
            messagebox.showinfo("Success", "Account created.")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Account already exists.")
        finally:
            conn.close()

    # ---------------- FORGOT PASSWORD ----------------
    def show_forgot_screen(self):
        self.clear_screen()

        tk.Label(self.container, text="RECOVER PASSWORD", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Label(self.container, text="Username").pack()
        user_entry = tk.Entry(self.container, width=25)
        user_entry.pack(pady=5)

        def verify_user():
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT security_question, security_answer FROM users WHERE username = ?",
                (user_entry.get(),)
            )
            result = cursor.fetchone()
            conn.close()

            if not result:
                messagebox.showerror("Error", "User not found.")
            else:
                self.show_reset_final(user_entry.get(), result[1], result[0])

        tk.Button(self.container, text="Verify", width=20, command=verify_user).pack(pady=10)
        tk.Button(self.container, text="Back", command=self.show_login_screen).pack()

    def show_reset_final(self, username, correct_answer, question):
        self.clear_screen()

        tk.Label(self.container, text=question, wraplength=350).pack(pady=10)
        answer_entry = tk.Entry(self.container, width=25)
        answer_entry.pack(pady=5)

        tk.Label(self.container, text="New Password").pack(pady=5)
        new_pw_entry = tk.Entry(self.container, show="*", width=25)
        new_pw_entry.pack(pady=5)

        def reset_password():
            if answer_entry.get().lower() != correct_answer.lower():
                messagebox.showerror("Error", "Incorrect answer.")
                return

            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (hash_password(new_pw_entry.get()), username)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Password updated.")
            self.show_login_screen()

        tk.Button(self.container, text="Update Password", width=20, command=reset_password).pack(pady=10)

    # ---------------- ADMIN MENU ----------------
    def show_admin_menu(self):
        """
        Admin Control Panel (GUI).
        Exposes existing admin capabilities:
        - View all users
        - Reset user password to default
        - Promote user to admin
        - Logout
        Core database logic remains unchanged.
        """
        self.clear_screen()

        tk.Label(
            self.container,
            text="ADMIN CONTROL PANEL",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # =========================
        # DATABASE VIEW (READ-ONLY)
        # =========================
        table_frame = tk.Frame(self.container)
        table_frame.pack(pady=10)

        tree = ttk.Treeview(
            table_frame,
            columns=("Username", "Role"),
            show="headings",
            height=8
        )
        tree.heading("Username", text="Username")
        tree.heading("Role", text="Role")
        tree.pack()

        # Populate table from existing database
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
        conn.close()

        # =========================
        # ADMIN ACTIONS
        # =========================
        action_frame = tk.Frame(self.container)
        action_frame.pack(pady=10)

        tk.Label(action_frame, text="Target Username:").grid(row=0, column=0, sticky="w")
        target_user = tk.Entry(action_frame, width=25)
        target_user.grid(row=0, column=1, pady=5)

        # --- Promote User to Admin ---
        def promote_user():
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET role = 'admin' WHERE username = ?",
                (target_user.get(),)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Admin", "User promoted to admin (if exists).")
            self.show_admin_menu()  # Refresh table

        # --- Reset User Password ---
        def reset_password():
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (hash_password("Temp123"), target_user.get())
            )
            conn.commit()
            conn.close()
            messagebox.showinfo(
                "Admin",
                "Password reset to default: Temp123"
            )

        tk.Button(
            action_frame,
            text="Promote to Admin",
            command=promote_user,
            width=20
        ).grid(row=1, column=0, pady=5)

        tk.Button(
            action_frame,
            text="Reset Password",
            command=reset_password,
            width=20
        ).grid(row=1, column=1, pady=5)

        # =========================
        # LOGOUT
        # =========================
        tk.Button(
            self.container,
            text="Logout",
            command=self.show_login_screen
        ).pack(pady=15)

    # EXIT / CLOSE HANDLER (GUI)
    def exit_program(self):
        """
        Safely closes the application.
        Asks for confirmation to prevent accidental exit.
        """
        if messagebox.askyesno(
            "Exit Application",
            "Are you sure you want to exit the program?"
        ):
            self.root.destroy()

# =========================
# START PROGRAM (GUI ENTRY POINT)
# =========================
if __name__ == "__main__":
    initialize_database()
    add_role_column_if_missing()
    create_default_admin()

    root = tk.Tk()
    App(root)
    root.mainloop()
