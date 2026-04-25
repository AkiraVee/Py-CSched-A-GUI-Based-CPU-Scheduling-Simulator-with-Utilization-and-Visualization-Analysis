"""
main_menu.py
====================
Main entry point for the CPU Scheduling Simulator.
"""

import tkinter as tk

# ── algorithm modules ─────────────────────────────────────
import fcfs_algorithm
import srtf_algorithm
import round_robin_algorithm
import np_priosched_algorithm
import pre_priosched_algorithm
import sjf_algorithm
# NEW: import admin panel from login file
from login_system import open_admin_panel

# ── design module ─────────────────────────────────────────
from menu_design import (
    BG, PANEL, ACCENT_G, ACCENT_B,
    algo_button,
    build_header,
    build_tab_bar,
    build_section_header,
    build_footer,
)


# ═══════════════════════════════════════════════════════════
#  ALGORITHM CALLBACKS
# ═══════════════════════════════════════════════════════════

def run_fcfs():
    fcfs_algorithm.fcfs_gui()

def run_sjf_np():
    sjf_algorithm.sjf_gui()

def run_priority_np():
    np_priosched_algorithm.priority_gui()

def run_sjf_preemptive():
    srtf_algorithm.srtf_gui()

def run_priority_preemptive():
    pre_priosched_algorithm.priority_preemptive_gui()

def run_rr():
    round_robin_algorithm.round_robin_gui()


# ═══════════════════════════════════════════════════════════
#  MAIN MENU WINDOW (FIXED)
# ═══════════════════════════════════════════════════════════

def open_main_menu(app):
    """
    Opens the main menu as a Toplevel window.
    """

    # 🔥 root is accessed via the app instance
    root = app.root
    menu = tk.Toplevel(root)
     # ✅ NEW: check admin role
    is_admin = getattr(app, "current_user_role", "user") == "admin" # added to differentiate admin from user
    menu.title("CPU Scheduling Simulator")
    menu.geometry("520x540")
    menu.resizable(False, False)
    menu.configure(bg=BG)

    # ── header ────────────────────────────────────────────
    build_header(menu)

    # ── content host ──────────────────────────────────────
    content_host = tk.Frame(menu, bg=BG)
    content_host.pack(fill="both", expand=True)

    # ── NON-PREEMPTIVE PANEL ─────────────────────────────
    np_panel = tk.Frame(content_host, bg=BG)

    build_section_header(
        np_panel,
        "NON-PREEMPTIVE ALGORITHMS",
        "process runs to completion",
        ACCENT_G
    )

    card_np = tk.Frame(np_panel, bg=PANEL)
    card_np.pack(fill="x", padx=16, pady=10)

    algo_button(card_np,
                "First Come First Serve",
                "FCFS  ·  Non-Preemptive  ·  Arrival-order execution",
                run_fcfs, ACCENT_G)

    algo_button(card_np,
                "Shortest Job First",
                "SJF   ·  Non-Preemptive  ·  Minimum burst time first",
                run_sjf_np, ACCENT_G)

    algo_button(card_np,
                "Priority Scheduling",
                "PRIO  ·  Non-Preemptive  ·  Highest priority executes first",
                run_priority_np, ACCENT_G)

    # ── PREEMPTIVE PANEL ─────────────────────────────────
    pre_panel = tk.Frame(content_host, bg=BG)

    build_section_header(
        pre_panel,
        "PREEMPTIVE ALGORITHMS",
        "process may be interrupted",
        ACCENT_B
    )

    card_pre = tk.Frame(pre_panel, bg=PANEL)
    card_pre.pack(fill="x", padx=16, pady=10)

    algo_button(card_pre,
                "Shortest Remaining Time First",
                "SRTF  ·  Preemptive  ·  Shortest remaining burst preempts",
                run_sjf_preemptive, ACCENT_B)

    algo_button(card_pre,
                "Priority Scheduling",
                "PRIO  ·  Preemptive  ·  Higher priority can preempt running",
                run_priority_preemptive, ACCENT_B)

    algo_button(card_pre,
                "Round Robin",
                "RR    ·  Preemptive  ·  Fixed time quantum rotation",
                run_rr, ACCENT_B)

    # ── TAB BAR ──────────────────────────────────────────
    build_tab_bar(menu, content_host, np_panel, pre_panel)

    # NEW: ADMIN PANEL (ONLY FOR ADMIN)
    if is_admin:
        admin_section = tk.Frame(content_host, bg=BG)
        admin_section.pack(fill="x")

        build_section_header(
            admin_section,
            "ADMIN PANEL",
            "system management tools",
            ACCENT_B
        )

        card_admin = tk.Frame(admin_section, bg=PANEL)
        card_admin.pack(fill="x", padx=16, pady=10)

        algo_button(card_admin,
                    "Open Admin Panel",
                    "Manage users, reset passwords, promote accounts",
                    lambda: open_admin_panel(app),
                    ACCENT_B)

    # ── FOOTER (FIXED EXIT BEHAVIOR) ─────────────────────
    build_footer(
        menu,
        on_exit=lambda: [menu.destroy(), app.show_login_screen(), root.deiconify()]
    )


# ═══════════════════════════════════════════════════════════
#  STANDALONE RUN (OPTIONAL)
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    # Mock app object for standalone testing
    class MockApp:
        def __init__(self, r): self.root = r
        def show_login_screen(self): print("Login screen refreshed")
    open_main_menu(MockApp(root))
    root.mainloop()