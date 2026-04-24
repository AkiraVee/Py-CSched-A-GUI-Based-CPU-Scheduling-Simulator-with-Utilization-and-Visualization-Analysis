import sqlite3
import hashlib
import os
import tkinter as tk
from tkinter import messagebox

# ── DESIGN SYSTEM ─────────────────────────────
from menu_design import (
    BG, PANEL, TEXT, SUBTEXT,
    ACCENT_B, ACCENT_G, ACCENT_R,
    MONO,
    build_header, build_footer,
    algo_button
)

import main_menu

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "users.db")

ADMIN_USERNAME = "admin"


# ═══════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════
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


def create_default_admin():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE username=?", (ADMIN_USERNAME,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users VALUES (?, ?, ?, ?, ?)
        """, (
            ADMIN_USERNAME,
            hash_password("admin123"),
            "default question",
            "admin",
            "admin"
        ))
        conn.commit()

    conn.close()


# ═══════════════════════════════════════════════
# GUI APPLICATION
# ═══════════════════════════════════════════════
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling System")
        self.root.geometry("520x540")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.container = tk.Frame(root, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    # ═══════════════════════════════════════════
    # LOGIN SCREEN
    # ═══════════════════════════════════════════
    def show_login_screen(self):
        self.clear()

        # HEADER
        build_header(self.container)

        # BODY
        body = tk.Frame(self.container, bg=BG)
        body.pack(fill="both", expand=True)

        center = tk.Frame(body, bg=BG)
        center.pack(expand=True)

        card = tk.Frame(center, bg=PANEL)
        card.pack(pady=20, padx=20)

        tk.Label(card,
                 text="SYSTEM LOGIN",
                 bg=PANEL, fg=TEXT,
                 font=(MONO, 14, "bold")).pack(pady=15)

        # Username
        tk.Label(card, text="USERNAME",
                 bg=PANEL, fg=SUBTEXT,
                 font=(MONO, 9)).pack(anchor="w", padx=30)

        self.u_entry = tk.Entry(card,
                                bg=BG, fg=TEXT,
                                insertbackground=TEXT,
                                relief="flat", width=28)
        self.u_entry.pack(pady=5)

        # Password
        tk.Label(card, text="PASSWORD",
                 bg=PANEL, fg=SUBTEXT,
                 font=(MONO, 9)).pack(anchor="w", padx=30)

        self.p_entry = tk.Entry(card,
                                show="*",
                                bg=BG, fg=TEXT,
                                insertbackground=TEXT,
                                relief="flat", width=28)
        self.p_entry.pack(pady=5)

        # BUTTONS (themed)
        algo_button(card,
                    "Login",
                    "Authenticate and open system",
                    self.handle_login,
                    ACCENT_B)

        algo_button(card,
                    "Create Account",
                    "Register a new user",
                    self.show_signup_screen,
                    ACCENT_G)

        # FOOTER (always visible)
        build_footer(self.container, on_exit=self.exit_program)

    # ═══════════════════════════════════════════
    # LOGIN LOGIC
    # ═══════════════════════════════════════════
    def handle_login(self):
        username = self.u_entry.get()
        password = self.p_entry.get()

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == hash_password(password):
            self.root.withdraw()
            main_menu.open_main_menu(self.root)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    # ═══════════════════════════════════════════
    # SIGNUP SCREEN
    # ═══════════════════════════════════════════
    def show_signup_screen(self):
        self.clear()

        build_header(self.container)

        body = tk.Frame(self.container, bg=BG)
        body.pack(fill="both", expand=True)

        center = tk.Frame(body, bg=BG)
        center.pack(expand=True)

        card = tk.Frame(center, bg=PANEL)
        card.pack(pady=20, padx=20)

        tk.Label(card,
                 text="CREATE ACCOUNT",
                 bg=PANEL, fg=TEXT,
                 font=(MONO, 14, "bold")).pack(pady=15)

        fields = ["Username", "Password", "Security Question", "Answer"]
        self.entries = {}

        for f in fields:
            tk.Label(card, text=f.upper(),
                     bg=PANEL, fg=SUBTEXT,
                     font=(MONO, 9)).pack(anchor="w", padx=30)

            e = tk.Entry(card,
                         show="*" if f == "Password" else "",
                         bg=BG, fg=TEXT,
                         insertbackground=TEXT,
                         relief="flat", width=28)
            e.pack(pady=5)
            self.entries[f] = e

        algo_button(card,
                    "Register",
                    "Create new account",
                    self.handle_signup,
                    ACCENT_B)

        algo_button(card,
                    "Back to Login",
                    "Return to login screen",
                    self.show_login_screen,
                    ACCENT_R)

        build_footer(self.container, on_exit=self.exit_program)

    # ═══════════════════════════════════════════
    # SIGNUP LOGIC
    # ═══════════════════════════════════════════
    def handle_signup(self):
        u = self.entries["Username"].get()
        p = self.entries["Password"].get()
        q = self.entries["Security Question"].get()
        a = self.entries["Answer"].get()

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                           (u, hash_password(p), q, a, "user"))
            conn.commit()
            messagebox.showinfo("Success", "Account created")
            self.show_login_screen()
        except:
            messagebox.showerror("Error", "User already exists")
        finally:
            conn.close()

    # ═══════════════════════════════════════════
    # EXIT
    # ═══════════════════════════════════════════
    def exit_program(self):
        self.root.destroy()


# ═══════════════════════════════════════════════
# RUN APP
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    initialize_database()
    create_default_admin()

    root = tk.Tk()
    App(root)
    root.mainloop()