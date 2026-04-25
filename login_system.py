import sqlite3
import hashlib
import os
import tkinter as tk
from tkinter import messagebox, ttk

from menu_design import (
    BG, PANEL, BORDER, TEXT, SUBTEXT,
    ACCENT_B, ACCENT_G, ACCENT_R, DIM, MONO,
    build_header, build_footer, h_rule,
    algo_button, styled_entry, styled_label,
    setup_treeview_style,
)

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "users.db")
ADMIN_USERNAME = "admin"


# ═══════════════════════════════════════════════════════════
#  DATABASE HELPERS
# ═══════════════════════════════════════════════════════════

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def initialize_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username          TEXT PRIMARY KEY,
            password          TEXT NOT NULL,
            security_question TEXT NOT NULL,
            security_answer   TEXT NOT NULL,
            role              TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    conn.close()


def create_default_admin():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username=?", (ADMIN_USERNAME,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (
            ADMIN_USERNAME,
            hash_password("admin123"),
            "Default admin question",
            "admin",
            "admin",
        ))
        conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════
#  ADMIN PANEL  (separate Toplevel)
# ═══════════════════════════════════════════════════════════

def open_admin_panel(app):
    setup_treeview_style()

    win = tk.Toplevel(app.root)
    win.title("Admin Control Panel")
    win.resizable(True, True)
    win.configure(bg=BG)
    win.state("zoomed")

    build_header(win)

    # ── title ─────────────────────────────────────────────
    tk.Label(win, text="ADMIN CONTROL PANEL",
             bg=BG, fg=TEXT,
             font=(MONO, 13, "bold")).pack(pady=(14, 4))
    h_rule(win, BORDER)

    # ── user table ────────────────────────────────────────
    table_frame = tk.Frame(win, bg=BG)
    table_frame.pack(fill="x", padx=20, pady=10)

    tree = ttk.Treeview(table_frame,
                        columns=("Username", "Role"),
                        show="headings",
                        height=8,
                        style="Dark.Treeview")
    tree.heading("Username", text="USERNAME")
    tree.heading("Role",     text="ROLE")
    tree.column("Username",  width=260, anchor="w")
    tree.column("Role",      width=120, anchor="center")
    tree.pack(fill="x")

    def _load():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
        conn.close()

    _load()

    h_rule(win, BORDER)

    # ── action area ───────────────────────────────────────
    action = tk.Frame(win, bg=BG, padx=20, pady=6)
    action.pack(fill="x")

    tk.Label(action, text="TARGET USERNAME",
             bg=BG, fg=SUBTEXT,
             font=(MONO, 8, "bold")).pack(anchor="w")

    target_entry = styled_entry(action, accent=ACCENT_G, width=32)
    target_entry.pack(anchor="w", pady=(4, 10))

    btn_frame = tk.Frame(action, bg=BG)
    btn_frame.pack(fill="x")

    def _promote():
        u = target_entry.get().strip()
        if not u:
            messagebox.showerror("Error", "Enter a username."); return
        if u == ADMIN_USERNAME:
            messagebox.showerror("Error", "Cannot modify the default admin."); return
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (u,))
        if not cursor.fetchone():
            conn.close(); messagebox.showerror("Error", "User not found."); return
        cursor.execute("UPDATE users SET role='admin' WHERE username=?", (u,))
        conn.commit(); conn.close()
        messagebox.showinfo("Admin", f"{u} promoted to admin.")
        target_entry.delete(0, "end")
        _load()

    def _unpromote():
        u = target_entry.get().strip()
        if not u:
            messagebox.showerror("Error", "Enter a username."); return
        if u == ADMIN_USERNAME:
            messagebox.showerror("Error", "Cannot demote the default admin."); return
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (u,))
        if not cursor.fetchone():
            conn.close(); messagebox.showerror("Error", "User not found."); return
        cursor.execute("UPDATE users SET role='user' WHERE username=?", (u,))
        conn.commit(); conn.close()
        messagebox.showinfo("Admin", f"{u} has been demoted to user.")
        target_entry.delete(0, "end")
        _load()

    def _reset():
        u = target_entry.get().strip()
        if not u:
            messagebox.showerror("Error", "Enter a username."); return
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (u,))
        if not cursor.fetchone():
            conn.close(); messagebox.showerror("Error", "User not found."); return
        cursor.execute("UPDATE users SET password=? WHERE username=?",
                       (hash_password("Temp123"), u))
        conn.commit(); conn.close()
        messagebox.showinfo("Admin", f"Password for {u} reset to: Temp123")
        target_entry.delete(0, "end")


    algo_button(btn_frame, "Promote to Admin",
                "Grant admin privileges to target user",
                _promote, ACCENT_G)
    algo_button(btn_frame, "Demote to User",
                "Remove admin privileges from target user",
                _unpromote, ACCENT_R)
    algo_button(btn_frame, "Reset Password",
                "Reset target user password to Temp123",
                _reset, ACCENT_B)

    def _close_panel():
        target_entry.delete(0, "end")
        win.destroy()
        app.root.deiconify()
        app.show_login()

    def _exit_app():
        target_entry.delete(0, "end")
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            win.destroy()
            app.root.destroy()

    h_rule(win, BORDER)
    foot = tk.Frame(win, bg=PANEL, padx=20, pady=10)
    foot.pack(fill="x", side="bottom")

    tk.Label(foot, text="●  ADMIN", bg=PANEL, fg=ACCENT_G,
             font=(MONO, 8)).pack(side="left")

    exit_btn = tk.Label(foot, text="[ EXIT APP ]", bg=PANEL, fg=ACCENT_R,
                        font=(MONO, 9, "bold"), padx=8, cursor="hand2")
    exit_btn.pack(side="right")
    exit_btn.bind("<Button-1>", lambda _: _exit_app())
    exit_btn.bind("<Enter>",    lambda _: exit_btn.configure(bg=ACCENT_R, fg=BG))
    exit_btn.bind("<Leave>",    lambda _: exit_btn.configure(bg=PANEL, fg=ACCENT_R))

    logout_btn = tk.Label(foot, text="[ LOGOUT ]", bg=PANEL, fg=ACCENT_B,
                          font=(MONO, 9, "bold"), padx=8, cursor="hand2")
    logout_btn.pack(side="right")
    logout_btn.bind("<Button-1>", lambda _: _close_panel())
    logout_btn.bind("<Enter>",    lambda _: logout_btn.configure(bg=ACCENT_B, fg=BG))
    logout_btn.bind("<Leave>",    lambda _: logout_btn.configure(bg=PANEL, fg=ACCENT_B))
    
    root.withdraw()  # hide main window until login is successful



# ═══════════════════════════════════════════════════════════
#  SHARED CARD BUILDER
# ═══════════════════════════════════════════════════════════

def _make_card(container, title):
    """Return a centred dark card frame with a title label."""
    center = tk.Frame(container, bg=BG)
    center.pack(expand=True)

    card = tk.Frame(center, bg=PANEL)
    card.pack(pady=20, padx=20)

    tk.Label(card, text=title,
             bg=PANEL, fg=TEXT,
             font=(MONO, 13, "bold")).pack(pady=(18, 6))

    h_rule(card, BORDER)
    return card


# ═══════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling System")
        self.root.geometry("520x580")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.container = tk.Frame(root, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    def show_login_screen(self):
        self.root.deiconify()
        self.show_login()

    def _clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def _body(self):
        """Return a fresh body frame after clearing and rebuilding the header."""
        self._clear()
        build_header(self.container)
        body = tk.Frame(self.container, bg=BG)
        body.pack(fill="both", expand=True)
        return body

    # ── LOGIN ─────────────────────────────────────────────
    def show_login(self):
        body = self._body()
        card = _make_card(body, "SYSTEM LOGIN")

        styled_label(card, "USERNAME")
        self.u_entry = styled_entry(card, accent=ACCENT_B)
        self.u_entry.pack(pady=(4, 8), padx=30)
        self.u_entry.delete(0, tk.END)

        styled_label(card, "PASSWORD")
        self.p_entry = styled_entry(card, show="*", accent=ACCENT_B)
        self.p_entry.pack(pady=(4, 12), padx=30)
        self.p_entry.delete(0, tk.END)

        algo_button(card, "Login",
                    "Authenticate and open the scheduler",
                    self._handle_login, ACCENT_B)
        algo_button(card, "Create Account",
                    "Register a new user account",
                    self.show_signup, ACCENT_G)
        algo_button(card, "Forgot Password",
                    "Recover access to your account",
                    self.show_forgot, ACCENT_R)

        build_footer(self.container, on_exit=self._exit)

    def _handle_login(self):
        u = self.u_entry.get().strip()
        p = self.p_entry.get()

        if not u or not p:
            messagebox.showerror("Login Failed", "Username and password cannot be empty.")
            return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username=?", (u,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == hash_password(p):
            if result[1] == "admin":
                open_admin_panel(self)
            else:
                self.root.withdraw()
                import main_menu
                main_menu.open_main_menu(self)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    # ── SIGN UP ───────────────────────────────────────────
    def show_signup(self):
        body = self._body()
        card = _make_card(body, "CREATE ACCOUNT")

        fields = ["USERNAME", "PASSWORD", "SECURITY QUESTION", "ANSWER"]
        shows  = {"PASSWORD": "*"}
        self._signup_entries = {}

        for f in fields:
            styled_label(card, f)
            e = styled_entry(card, show=shows.get(f, ""), accent=ACCENT_G)
            e.pack(pady=(4, 8), padx=30)
            self._signup_entries[f] = e

        algo_button(card, "Register",
                    "Create your account",
                    self._handle_signup, ACCENT_G)
        algo_button(card, "Back",
                    "Return to login",
                    self.show_login, ACCENT_R)

        build_footer(self.container, on_exit=self._exit)

    def _handle_signup(self):
        u = self._signup_entries["USERNAME"].get().strip()
        p = self._signup_entries["PASSWORD"].get()
        q = self._signup_entries["SECURITY QUESTION"].get().strip()
        a = self._signup_entries["ANSWER"].get().strip()

        if not all([u, p, q, a]):
            messagebox.showerror("Error", "All fields are required."); return
        if u.lower() == ADMIN_USERNAME:
            messagebox.showerror("Error", "That username is reserved."); return
        if len(p) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters."); return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                           (u, hash_password(p), q, a, "user"))
            conn.commit()
            messagebox.showinfo("Success", "Account created.")
            self.show_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        finally:
            conn.close()

    # ── FORGOT PASSWORD ───────────────────────────────────
    def show_forgot(self):
        body = self._body()
        card = _make_card(body, "RECOVER ACCOUNT")

        styled_label(card, "USERNAME")
        self._forgot_entry = styled_entry(card, accent=ACCENT_B)
        self._forgot_entry.pack(pady=(4, 12), padx=30)

        algo_button(card, "Next",
                    "Look up your security question",
                    self._verify_user, ACCENT_B)
        algo_button(card, "Back",
                    "Return to login",
                    self.show_login, ACCENT_R)

        build_footer(self.container, on_exit=self._exit)

    def _verify_user(self):
        u = self._forgot_entry.get().strip()
        if not u:
            messagebox.showerror("Error", "Enter your username."); return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT security_question, security_answer FROM users WHERE username=?", (u,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Error", "User not found."); return

        self._show_security_q(u, row[0], row[1])

    def _show_security_q(self, username, question, correct_answer):
        body = self._body()
        card = _make_card(body, "SECURITY CHECK")

        tk.Label(card, text=question,
                 bg=PANEL, fg=ACCENT_B,
                 font=(MONO, 10), wraplength=320,
                 justify="center").pack(pady=(10, 4), padx=30)

        styled_label(card, "YOUR ANSWER")
        self._answer_entry = styled_entry(card, accent=ACCENT_B)
        self._answer_entry.pack(pady=(4, 12), padx=30)

        algo_button(card, "Verify",
                    "Check your security answer",
                    lambda: self._verify_answer(username, correct_answer),
                    ACCENT_B)
        algo_button(card, "Back",
                    "Return to account recovery",
                    self.show_forgot, ACCENT_R)

        build_footer(self.container, on_exit=self._exit)

    def _verify_answer(self, username, correct_answer):
        ans = self._answer_entry.get().strip()
        if not ans:
            messagebox.showerror("Error", "Enter your answer."); return
        if ans.lower() != correct_answer.lower():
            messagebox.showerror("Error", "Incorrect answer."); return
        self._show_new_password(username)

    def _show_new_password(self, username):
        body = self._body()
        card = _make_card(body, "SET NEW PASSWORD")

        styled_label(card, "NEW PASSWORD")
        self._new_pw = styled_entry(card, show="*", accent=ACCENT_G)
        self._new_pw.pack(pady=(4, 8), padx=30)

        styled_label(card, "CONFIRM PASSWORD")
        self._confirm_pw = styled_entry(card, show="*", accent=ACCENT_G)
        self._confirm_pw.pack(pady=(4, 12), padx=30)

        algo_button(card, "Update Password",
                    "Save your new password",
                    lambda: self._update_password(username),
                    ACCENT_G)

        build_footer(self.container, on_exit=self._exit)

    def _update_password(self, username):
        pw  = self._new_pw.get()
        cpw = self._confirm_pw.get()

        if not pw or not cpw:
            messagebox.showerror("Error", "Password fields cannot be empty."); return
        if len(pw) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters."); return
        if pw != cpw:
            messagebox.showerror("Error", "Passwords do not match."); return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password=? WHERE username=?",
                       (hash_password(pw), username))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Password updated.")
        self.show_login()

    # ── EXIT ──────────────────────────────────────────────
    def _exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        initialize_database()
        create_default_admin()


        root = tk.Tk()
        App(root)
        root.mainloop()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")  # keeps the terminal open so you can read the error