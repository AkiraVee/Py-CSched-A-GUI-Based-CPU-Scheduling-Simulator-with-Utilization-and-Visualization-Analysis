"""
main_menu.py
====================
Main entry point for the CPU Scheduling Simulator.

This file is responsible only for application logic:
  - Defining which algorithm function to call for each button
  - Building the two content panels (Non-Preemptive and Preemptive)
  - Assembling the window using builders from menu_design.py

All colours, fonts, and widget styling live in menu_design.py.
All algorithm logic and GUI windows live in their respective algorithm files.
"""

import tkinter as tk

# ── algorithm modules ─────────────────────────────────────
# Each module exposes a *_gui() function that opens its own
# themed Toplevel window for data entry and output display.
import fcfs_algorithm
import srtf_algorithm
import round_robin_algorithm
import np_priosched_algorithm
import pre_priosched_algorithm
import sjf_algorithm

# ── design module ─────────────────────────────────────────
# Import all visual constants and widget builder functions.
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
#  Each function is a thin wrapper that opens the corresponding
#  algorithm's GUI window.  Kept separate so they can be passed
#  as command references without lambda closures.
# ═══════════════════════════════════════════════════════════

def run_fcfs():
    """Open the First Come First Serve (Non-Preemptive) GUI."""
    fcfs_algorithm.fcfs_gui()

def run_sjf_np():
    """Open the Shortest Job First (Non-Preemptive) GUI."""
    sjf_algorithm.sjf_gui()

def run_priority_np():
    """Open the Priority Scheduling (Non-Preemptive) GUI."""
    np_priosched_algorithm.priority_gui()

def run_sjf_preemptive():
    """Open the Shortest Remaining Time First (Preemptive) GUI."""
    srtf_algorithm.srtf_gui()

def run_priority_preemptive():
    """Open the Priority Scheduling (Preemptive) GUI."""
    pre_priosched_algorithm.priority_preemptive_gui()

def run_rr():
    """Open the Round Robin (Preemptive) GUI."""
    round_robin_algorithm.round_robin_gui()


# ═══════════════════════════════════════════════════════════
#  MAIN MENU WINDOW
# ═══════════════════════════════════════════════════════════

def open_main_menu():
    """
    Build and display the main menu Toplevel window.

    Window layout (top → bottom):
      1. Header  – accent bar + title + version   (menu_design.build_header)
      2. Tab bar – NON-PREEMPTIVE / PREEMPTIVE    (menu_design.build_tab_bar)
      3. Content – one of two panels shown at a time
      4. Footer  – status dot + EXIT button       (menu_design.build_footer)
    """

    # ── window setup ──────────────────────────────────────
    menu = tk.Toplevel()
    menu.title("CPU Scheduling Simulator")
    menu.geometry("520x540")
    menu.resizable(False, False)
    menu.configure(bg=BG)

    # ── 1. header ─────────────────────────────────────────
    build_header(menu)

    # ── content host ──────────────────────────────────────
    # Both panels are placed inside this frame using .place()
    # so they stack on top of each other; only one is visible.
    content_host = tk.Frame(menu, bg=BG)
    content_host.pack(fill="both", expand=True)

    # ── 2a. NON-PREEMPTIVE panel ──────────────────────────
    # Contains three non-preemptive scheduling algorithms.
    np_panel = tk.Frame(content_host, bg=BG)

    # section label at the top of the panel
    build_section_header(np_panel,
                         "NON-PREEMPTIVE ALGORITHMS",
                         "process runs to completion",
                         ACCENT_G)

    # card frame groups the algorithm rows visually
    card_np = tk.Frame(np_panel, bg=PANEL)
    card_np.pack(fill="x", padx=16, pady=10)

    # individual algorithm rows – each glows green on hover
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

    # ── 2b. PREEMPTIVE panel ──────────────────────────────
    # Contains three preemptive scheduling algorithms.
    pre_panel = tk.Frame(content_host, bg=BG)

    # section label at the top of the panel
    build_section_header(pre_panel,
                         "PREEMPTIVE ALGORITHMS",
                         "process may be interrupted",
                         ACCENT_B)

    # card frame groups the algorithm rows visually
    card_pre = tk.Frame(pre_panel, bg=PANEL)
    card_pre.pack(fill="x", padx=16, pady=10)

    # individual algorithm rows – each glows cyan on hover
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

    # ── 3. tab bar ────────────────────────────────────────
    # Must be built AFTER panels exist so the switcher can
    # reference them.  Packed before content_host in the widget
    # stacking order via the tab_bar internal pack call.
    build_tab_bar(menu, content_host, np_panel, pre_panel)

    # ── 4. footer ─────────────────────────────────────────
    # Destroys only the menu Toplevel (not the hidden root).
    build_footer(menu, on_exit=menu.destroy)


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
#  When run directly, create a hidden root window (required
#  by Tkinter) then open the main menu Toplevel.
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()      # hide the blank root window
    open_main_menu()
    root.mainloop()