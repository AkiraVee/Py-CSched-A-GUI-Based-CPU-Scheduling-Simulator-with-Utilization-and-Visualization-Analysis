import sqlite3
import hashlib
import os
import tkinter as tk
from tkinter import messagebox, ttk # needed for the admin table

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


# ═════════════════ DATABASE ═════════════════
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


# NEW: ADMIN CONTROL PANEL
def open_admin_panel(app):
    from menu_design import setup_treeview_style
    setup_treeview_style()  # added this so it call once

    admin_win = tk.Toplevel(app.root)
    admin_win.title("Admin Control Panel")
    admin_win.geometry("520x540")
    admin_win.configure(bg=BG)

    build_header(admin_win)

    container = tk.Frame(admin_win, bg=BG)
    container.pack(fill="both", expand=True, side="top")  # keep footer visible

    tk.Label(
        container,
        text="ADMIN CONTROL PANEL",
        bg=BG, fg=TEXT,
        font=(MONO, 14, "bold")
    ).pack(pady=10)

    # ── USER TABLE ─────────────────────────
    table_frame = tk.Frame(container, bg=BG)
    table_frame.pack(pady=10)

    tree = ttk.Treeview(
    table_frame,
    columns=("Username", "Role"),
    show="headings",
    height=12,
    style="Dark.Treeview"
    )
    
    tree.heading("Username", text="Username")
    tree.heading("Role", text="Role")

    tree.column("Username", width=220, anchor="w")
    tree.column("Role", width=100, anchor="center")

    tree.pack(fill="x", expand=True)

    def load_users():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
        conn.close()

    load_users()

    # ── ACTIONS ────────────────────────────
    action_frame = tk.Frame(container, bg=BG)
    action_frame.pack(pady=10)

    # grid-only subframe
    form_frame = tk.Frame(action_frame, bg=BG)
    form_frame.pack()

    tk.Label(
        form_frame,
        text="Target Username:",
        bg=BG, fg=TEXT
    ).grid(row=0, column=0, padx=5, pady=5)

    target_user = tk.Entry(form_frame)
    target_user.grid(row=0, column=1, padx=5, pady=5)

    # pack-only subframe
    button_frame = tk.Frame(action_frame, bg=BG)
    button_frame.pack(pady=10)

    def promote_user():
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET role='admin' WHERE username=?",
            (target_user.get(),)
        )
        conn.commit()
        conn.close()
        load_users()

    def reset_password():
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password=? WHERE username=?",
            (hash_password("Temp123"), target_user.get())
        )
        conn.commit()
        conn.close()

    algo_button(
        button_frame,          # FIXED
        "Promote to Admin",
        "Grant admin privileges",
        promote_user,
        ACCENT_G
    )

    algo_button(
        button_frame,          # FIXED
        "Reset Password",
        "Reset to Temp123",
        reset_password,
        ACCENT_B
    )

    build_footer(admin_win, on_exit=admin_win.destroy)

# ═════════════════ APP ═════════════════
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

    # ═════════ LOGIN SCREEN ═════════
    def show_login_screen(self):
        self.clear()

        build_header(self.container)

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

        tk.Label(card, text="USERNAME",
                 bg=PANEL, fg=SUBTEXT,
                 font=(MONO, 9)).pack(anchor="w", padx=30)

        self.u_entry = tk.Entry(card,
                                bg=BG, fg=TEXT,
                                insertbackground=TEXT,
                                relief="flat", width=28)
        self.u_entry.pack(pady=5)
        self.u_entry.delete(0, tk.END)

        tk.Label(card, text="PASSWORD",
                 bg=PANEL, fg=SUBTEXT,
                 font=(MONO, 9)).pack(anchor="w", padx=30)

        self.p_entry = tk.Entry(card,
                                show="*",
                                bg=BG, fg=TEXT,
                                insertbackground=TEXT,
                                relief="flat", width=28)
        self.p_entry.pack(pady=5)
        self.p_entry.delete(0, tk.END)

        # LOGIN BUTTONS
        algo_button(card, "Login",
                    "Authenticate and open system",
                    self.handle_login,
                    ACCENT_B)

        algo_button(card, "Create Account",
                    "Register new user",
                    self.show_signup_screen,
                    ACCENT_G)

        algo_button(card, "Forgot Password",
                    "Recover account access",
                    self.show_forgot_screen,
                    ACCENT_R)

        build_footer(self.container, on_exit=self.exit_program)

    # ═════════ LOGIN LOGIC ═════════
    def handle_login(self):
        u = self.u_entry.get()
        p = self.p_entry.get()

         # ── Reject login if username or password fields are empty ──
        if not u or not p:
            messagebox.showerror("Login Failed", "Username and password cannot be empty")
            return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (u,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == hash_password(p):
            self.root.withdraw()

            # ✅ NEW: admin routed first
            if result[1] == "admin":
                open_admin_panel(self)
                return   # STOP HERE for admin
            
            main_menu.open_main_menu(self)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    # ═════════ SIGNUP SCREEN ═════════
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

        algo_button(card, "Register",
                    "Create account",
                    self.handle_signup,
                    ACCENT_B)

        algo_button(card, "Back",
                    "Return to login",
                    self.show_login_screen,
                    ACCENT_R)

        build_footer(self.container, on_exit=self.exit_program)

    def handle_signup(self):
        u = self.entries["Username"].get()
        p = self.entries["Password"].get()
        q = self.entries["Security Question"].get()
        a = self.entries["Answer"].get()

         # ── Reject registration if any field is left blank ──
        if not u or not p or not q or not a:
            messagebox.showerror("Registration Failed", "All fields must be filled out")
            return

        # ── Enforce a minimum password length of 6 characters ──
        if len(p) < 6:
            messagebox.showerror("Registration Failed", "Password must be at least 6 characters")
            return

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

    # ═════════ FORGOT PASSWORD FLOW ═════════
    def show_forgot_screen(self):
        self.clear()

        build_header(self.container)

        body = tk.Frame(self.container, bg=BG)
        body.pack(fill="both", expand=True)

        center = tk.Frame(body, bg=BG)
        center.pack(expand=True)

        card = tk.Frame(center, bg=PANEL)
        card.pack(pady=20, padx=20)

        tk.Label(card,
                 text="RECOVER ACCOUNT",
                 bg=PANEL, fg=TEXT,
                 font=(MONO, 14, "bold")).pack(pady=15)

        tk.Label(card, text="USERNAME",
                 bg=PANEL, fg=SUBTEXT).pack(anchor="w", padx=30)

        self.f_user = tk.Entry(card,
                               bg=BG, fg=TEXT,
                               insertbackground=TEXT,
                               relief="flat", width=28)
        self.f_user.pack(pady=5)

        algo_button(card,
                    "Next",
                    "Verify username",
                    self.verify_user_for_reset,
                    ACCENT_B)

        algo_button(card,
                    "Back",
                    "Return to login",
                    self.show_login_screen,
                    ACCENT_R)

        build_footer(self.container, on_exit=self.exit_program)

    def verify_user_for_reset(self):
        username = self.f_user.get()

         # ── Reject if username field is empty before querying the database ──
        if not username:
            messagebox.showerror("Error", "Username cannot be empty")
            return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT security_question, security_answer FROM users WHERE username=?", (username,))
        data = cursor.fetchone()
        conn.close()

        if not data:
            messagebox.showerror("Error", "User not found")
            return

        self.show_security_question(username, data[0], data[1])

    def show_security_question(self, username, question, answer):
        self.clear()

        build_header(self.container)

        body = tk.Frame(self.container, bg=BG)
        body.pack(fill="both", expand=True)

        center = tk.Frame(body, bg=BG)
        center.pack(expand=True)

        card = tk.Frame(center, bg=PANEL)
        card.pack(pady=20, padx=20)

        tk.Label(card,
                 text=question,
                 bg=PANEL, fg=TEXT,
                 wraplength=300,
                 font=(MONO, 10)).pack(pady=15)

        self.sec_answer = tk.Entry(card,
                                   bg=BG, fg=TEXT,
                                   insertbackground=TEXT,
                                   relief="flat", width=28)
        self.sec_answer.pack(pady=5)

        algo_button(card,
                    "Verify",
                    "Check security answer",
                    lambda: self.verify_answer(username, answer),
                    ACCENT_B)

        build_footer(self.container, on_exit=self.exit_program)

    def verify_answer(self, username, correct):
        # ── Reject if the security answer field is left blank ──
        if not self.sec_answer.get():
            messagebox.showerror("Error", "Answer cannot be empty")
            return

        if self.sec_answer.get().lower() != correct.lower():
            messagebox.showerror("Error", "Wrong answer")
            return

        self.show_new_password(username)

    def show_new_password(self, username):
        self.clear()

        build_header(self.container)

        body = tk.Frame(self.container, bg=BG)
        body.pack(fill="both", expand=True)

        center = tk.Frame(body, bg=BG)
        center.pack(expand=True)

        card = tk.Frame(center, bg=PANEL)
        card.pack(pady=20, padx=20)

        tk.Label(card, text="NEW PASSWORD",
                 bg=PANEL, fg=TEXT,
                 font=(MONO, 14, "bold")).pack(pady=15)

        self.new_pw = tk.Entry(card, show="*",
                               bg=BG, fg=TEXT,
                               insertbackground=TEXT,
                               relief="flat", width=28)
        self.new_pw.pack(pady=5)

        self.confirm_pw = tk.Entry(card, show="*",
                                   bg=BG, fg=TEXT,
                                   insertbackground=TEXT,
                                   relief="flat", width=28)
        self.confirm_pw.pack(pady=5)

        algo_button(card,
                    "Update Password",
                    "Save new password",
                    lambda: self.update_password(username),
                    ACCENT_G)

        build_footer(self.container, on_exit=self.exit_program)

    def update_password(self, username):
        # ── Reject if either password field is blank before checking match ──
        if not self.new_pw.get() or not self.confirm_pw.get():
            messagebox.showerror("Error", "Password fields cannot be empty")
            return

        # ── Enforce a minimum password length of 6 characters on reset ──
        if len(self.new_pw.get()) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        if self.new_pw.get() != self.confirm_pw.get():
            messagebox.showerror("Error", "Passwords do not match")
            return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password=? WHERE username=?",
                       (hash_password(self.new_pw.get()), username))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Password updated")
        self.show_login_screen()

    # ═════════ EXIT ═════════
    def exit_program(self):
        self.root.destroy()


# ═════════ RUN ═════════
if __name__ == "__main__":
    initialize_database()
    create_default_admin()

    root = tk.Tk()
    App(root)
    root.mainloop()