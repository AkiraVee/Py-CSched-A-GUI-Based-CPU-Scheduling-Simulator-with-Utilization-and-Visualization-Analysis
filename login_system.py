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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "users.db")

ADMIN_USERNAME = "admin"

def display_header(title):
    print("\n==============================")
    print(f"{title:^30}")
    print("==============================")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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

def add_role_column_if_missing():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [c[1] for c in cursor.fetchall()]
    if "role" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        conn.commit()
    conn.close()

def create_default_admin():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (ADMIN_USERNAME,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (
                username, password, security_question, security_answer, role
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
        
        tk.Button(self.container, text="Exit", width=20, fg="red", command=self.exit_program).pack(pady=8)

    def handle_login(self):
        username = self.u_entry.get()
        password = self.p_entry.get()

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
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
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                           (u, hash_password(p), q, a, "user"))
            conn.commit()
            messagebox.showinfo("Success", "Account created.")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Account already exists.")
        finally:
            conn.close()

    # ---------------- FORGOT PASSWORD FLOW ----------------
    def show_forgot_screen(self):
        self.clear_screen()

        tk.Label(self.container, text="RECOVER PASSWORD", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Label(self.container, text="Enter Username").pack(pady=5)
        
        self.forgot_user_entry = tk.Entry(self.container, width=25)
        self.forgot_user_entry.pack(pady=5)

        tk.Button(self.container, text="Next", width=20, 
                  command=self.verify_username_for_reset).pack(pady=10)
        tk.Button(self.container, text="Back", command=self.show_login_screen).pack()

    def verify_username_for_reset(self):
        username = self.forgot_user_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT security_question, security_answer FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            messagebox.showerror("Error", "User not found.")
            return

        # Go to security question screen
        self.show_security_question_screen(username, result[0], result[1])

    def show_security_question_screen(self, username, question, correct_answer):
        self.clear_screen()

        tk.Label(self.container, text="RECOVER PASSWORD", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.container, text=question, wraplength=350, justify="center").pack(pady=15)

        tk.Label(self.container, text="Your Answer:").pack()
        self.answer_entry = tk.Entry(self.container, width=30)
        self.answer_entry.pack(pady=8)

        tk.Button(
            self.container,
            text="Verify Answer",
            width=20,
            command=lambda: self.verify_security_answer(username, correct_answer)
        ).pack(pady=15)

        tk.Button(self.container, text="Back", command=self.show_forgot_screen).pack()

    def verify_security_answer(self, username, correct_answer):
        user_answer = self.answer_entry.get().strip()

        if not user_answer:
            messagebox.showerror("Error", "Please enter your answer.")
            return

        if user_answer.lower() != correct_answer.lower():
            messagebox.showerror("Error", "Incorrect security answer.")
            return

        # Correct answer → Move to NEW password screen
        messagebox.showinfo("Success", "Security answer verified!\nNow set your new password.")
        self.show_new_password_screen(username)

    def show_new_password_screen(self, username):
        """New dedicated screen for entering new password"""
        self.clear_screen()

        tk.Label(self.container, text="SET NEW PASSWORD", font=("Arial", 16, "bold")).pack(pady=15)
        
        tk.Label(self.container, text="Enter your new password:").pack(pady=5)
        self.new_pw_entry = tk.Entry(self.container, show="*", width=30)
        self.new_pw_entry.pack(pady=8)

        tk.Label(self.container, text="Confirm new password:").pack(pady=5)
        self.confirm_pw_entry = tk.Entry(self.container, show="*", width=30)
        self.confirm_pw_entry.pack(pady=8)

        button_frame = tk.Frame(self.container)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Update Password",
            width=18,
            command=lambda: self.reset_password(username)
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            button_frame,
            text="Back",
            width=18,
            command=lambda: self.show_security_question_screen(
                username, 
                self.get_question_for_user(username), 
                self.get_answer_for_user(username)
            )
        ).grid(row=0, column=1, padx=8)

    def get_question_for_user(self, username):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT security_question FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else ""

    def get_answer_for_user(self, username):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT security_answer FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else ""

    def reset_password(self, username):
        new_password = self.new_pw_entry.get()
        confirm_password = self.confirm_pw_entry.get()

        if not new_password:
            messagebox.showerror("Error", "Please enter a new password.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hash_password(new_password), username)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Password has been updated successfully.")
        self.show_login_screen()

    # ---------------- ADMIN MENU ----------------
    def show_admin_menu(self):
        self.clear_screen()

        tk.Label(self.container, text="ADMIN CONTROL PANEL", 
                 font=("Arial", 16, "bold")).pack(pady=10)

        table_frame = tk.Frame(self.container)
        table_frame.pack(pady=10)

        tree = ttk.Treeview(table_frame, columns=("Username", "Role"), show="headings", height=8)
        tree.heading("Username", text="Username")
        tree.heading("Role", text="Role")
        tree.pack()

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
        conn.close()

        action_frame = tk.Frame(self.container)
        action_frame.pack(pady=10)

        tk.Label(action_frame, text="Target Username:").grid(row=0, column=0, sticky="w")
        target_user = tk.Entry(action_frame, width=25)
        target_user.grid(row=0, column=1, pady=5)

        def promote_user():
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET role = 'admin' WHERE username = ?", (target_user.get(),))
            conn.commit()
            conn.close()
            messagebox.showinfo("Admin", "User promoted to admin (if exists).")
            self.show_admin_menu()

        def reset_password():
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE username = ?",
                           (hash_password("Temp123"), target_user.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Admin", "Password reset to default: Temp123")

        tk.Button(action_frame, text="Promote to Admin", command=promote_user, width=20).grid(row=1, column=0, pady=5)
        tk.Button(action_frame, text="Reset Password", command=reset_password, width=20).grid(row=1, column=1, pady=5)

        tk.Button(self.container, text="Logout", command=self.show_login_screen).pack(pady=15)

    def exit_program(self):
        if messagebox.askyesno("Exit Application", "Are you sure you want to exit the program?"):
            self.root.destroy()


# =========================
# START PROGRAM
# =========================
if __name__ == "__main__":
    initialize_database()
    add_role_column_if_missing()
    create_default_admin()

    root = tk.Tk()
    App(root)
    root.mainloop()