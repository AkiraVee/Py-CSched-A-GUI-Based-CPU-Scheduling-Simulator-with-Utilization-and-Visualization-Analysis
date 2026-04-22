import tkinter as tk
from tkinter import ttk

import fcfs_algorithm
import srtf_algorithm
import round_robin_algorithm
import npp_algorithm
import pp_algorithm
import sjf_algorithm


# ═══════════════════════════════════════════════════════════
#  PALETTE
# ═══════════════════════════════════════════════════════════
BG        = "#080b10"       # near-black background
PANEL     = "#0e1218"       # card background
BORDER    = "#1c2333"       # subtle border
ACCENT_G  = "#00ffa3"       # neon green  – Non-Preemptive
ACCENT_B  = "#00c8ff"       # neon cyan   – Preemptive
ACCENT_R  = "#ff4d6d"       # neon red    – Exit
DIM       = "#3a4255"       # muted/inactive
TEXT      = "#d0d8e8"       # primary text
SUBTEXT   = "#5a6275"       # secondary text
MONO      = "Consolas"


# ═══════════════════════════════════════════════════════════
#  NON-PREEMPTIVE CALLBACKS  (unchanged)
# ═══════════════════════════════════════════════════════════
def run_fcfs():            fcfs_algorithm.fcfs_gui()
def run_sjf_np():          sjf_algorithm.sjf_gui()
def run_priority_np():     npp_algorithm.priority_gui()

# ═══════════════════════════════════════════════════════════
#  PREEMPTIVE CALLBACKS  (unchanged)
# ═══════════════════════════════════════════════════════════
def run_sjf_preemptive():      srtf_algorithm.srtf_gui()
def run_priority_preemptive(): pp_algorithm.priority_preemptive_gui()
def run_rr():                  round_robin_algorithm.round_robin_gui()


# ═══════════════════════════════════════════════════════════
#  REUSABLE WIDGETS
# ═══════════════════════════════════════════════════════════

def _h_rule(parent, color=BORDER):
    """A single-pixel horizontal divider."""
    tk.Frame(parent, bg=color, height=1).pack(fill="x")


def _algo_button(parent, label, desc, command, accent):
    """
    One algorithm row:  [accent bar | label + desc | arrow]
    """
    row = tk.Frame(parent, bg=PANEL, cursor="hand2")
    row.pack(fill="x", padx=24, pady=4)

    # left accent stripe
    tk.Frame(row, bg=accent, width=3).pack(side="left", fill="y")

    inner = tk.Frame(row, bg=PANEL)
    inner.pack(side="left", fill="both", expand=True, padx=14, pady=10)

    tk.Label(inner, text=label, bg=PANEL, fg=TEXT,
             font=(MONO, 11, "bold"), anchor="w").pack(fill="x")
    tk.Label(inner, text=desc, bg=PANEL, fg=SUBTEXT,
             font=(MONO, 8), anchor="w").pack(fill="x")

    arrow = tk.Label(row, text="›", bg=PANEL, fg=DIM,
                     font=(MONO, 18), padx=12)
    arrow.pack(side="right")

    def _get_all(w):
        widgets = [w]
        try:
            for child in w.winfo_children():
                widgets += _get_all(child)
        except Exception:
            pass
        return widgets

    def _enter(_):
        for w in _get_all(row):
            try: w.configure(bg=BORDER)
            except Exception: pass
        arrow.configure(fg=accent)

    def _leave(_):
        for w in _get_all(row):
            try: w.configure(bg=PANEL)
            except Exception: pass
        arrow.configure(fg=DIM)

    def _click(_):
        command()

    for w in _get_all(row):
        w.bind("<Enter>",    _enter)
        w.bind("<Leave>",    _leave)
        w.bind("<Button-1>", _click)

    _h_rule(parent, BORDER)
    return row


# ═══════════════════════════════════════════════════════════
#  MAIN MENU
# ═══════════════════════════════════════════════════════════
def open_main_menu():
    menu = tk.Toplevel()
    menu.title("CPU Scheduling Simulator")
    menu.geometry("520x540")
    menu.resizable(False, False)
    menu.configure(bg=BG)

    # ── top bar ──────────────────────────────────────────
    topbar = tk.Frame(menu, bg=PANEL)
    topbar.pack(fill="x")

    tk.Frame(topbar, bg=ACCENT_G, height=2).pack(fill="x")   # glowing top line

    hdr = tk.Frame(topbar, bg=PANEL, padx=24, pady=16)
    hdr.pack(fill="x")

    tk.Label(hdr, text="◈  CPU SCHEDULING SIMULATOR",
             bg=PANEL, fg=TEXT,
             font=(MONO, 14, "bold")).pack(side="left")

    tk.Label(hdr, text="v1.0",
             bg=PANEL, fg=SUBTEXT,
             font=(MONO, 9)).pack(side="right", pady=4)

    _h_rule(menu, BORDER)

    # ── tab bar ──────────────────────────────────────────
    tab_bar = tk.Frame(menu, bg=PANEL)
    tab_bar.pack(fill="x")

    content_host = tk.Frame(menu, bg=BG)
    content_host.pack(fill="both", expand=True)

    # ── content panels ────────────────────────────────────
    def _make_panel():
        return tk.Frame(content_host, bg=BG)

    # NON-PREEMPTIVE panel
    np_panel = _make_panel()

    sec_hdr = tk.Frame(np_panel, bg=BG, padx=24, pady=14)
    sec_hdr.pack(fill="x")
    tk.Label(sec_hdr, text="NON-PREEMPTIVE ALGORITHMS",
             bg=BG, fg=ACCENT_G,
             font=(MONO, 9, "bold")).pack(side="left")
    tk.Label(sec_hdr, text="process runs to completion",
             bg=BG, fg=SUBTEXT,
             font=(MONO, 8)).pack(side="right")
    _h_rule(np_panel, BORDER)

    _algo_button(np_panel,
                 "First Come First Serve",
                 "FCFS  ·  Non-Preemptive  ·  Arrival-order execution",
                 run_fcfs, ACCENT_G)
    _algo_button(np_panel,
                 "Shortest Job First",
                 "SJF   ·  Non-Preemptive  ·  Minimum burst time first",
                 run_sjf_np, ACCENT_G)
    _algo_button(np_panel,
                 "Priority Scheduling",
                 "PRIO  ·  Non-Preemptive  ·  Highest priority executes first",
                 run_priority_np, ACCENT_G)

    # PREEMPTIVE panel
    pre_panel = _make_panel()

    sec_hdr2 = tk.Frame(pre_panel, bg=BG, padx=24, pady=14)
    sec_hdr2.pack(fill="x")
    tk.Label(sec_hdr2, text="PREEMPTIVE ALGORITHMS",
             bg=BG, fg=ACCENT_B,
             font=(MONO, 9, "bold")).pack(side="left")
    tk.Label(sec_hdr2, text="process may be interrupted",
             bg=BG, fg=SUBTEXT,
             font=(MONO, 8)).pack(side="right")
    _h_rule(pre_panel, BORDER)

    _algo_button(pre_panel,
                 "Shortest Remaining Time First",
                 "SRTF  ·  Preemptive  ·  Shortest remaining burst preempts",
                 run_sjf_preemptive, ACCENT_B)
    _algo_button(pre_panel,
                 "Priority Scheduling",
                 "PRIO  ·  Preemptive  ·  Higher priority can preempt running",
                 run_priority_preemptive, ACCENT_B)
    _algo_button(pre_panel,
                 "Round Robin",
                 "RR    ·  Preemptive  ·  Fixed time quantum rotation",
                 run_rr, ACCENT_B)

    # ── tab switching logic ───────────────────────────────
    _active = [None]

    def _show(panel, btn_self, accent, other_btn):
        panel.place(relx=0, rely=0, relwidth=1, relheight=1)
        if _active[0] and _active[0] is not panel:
            _active[0].place_forget()
        _active[0] = panel
        btn_self.configure(fg=accent, bg=BG)
        other_btn.configure(fg=DIM, bg=PANEL)

    tab_np  = tk.Label(tab_bar, text="NON-PREEMPTIVE", bg=PANEL, fg=ACCENT_G,
                       font=(MONO, 10, "bold"), padx=18, pady=10, cursor="hand2")
    tab_pre = tk.Label(tab_bar, text="PREEMPTIVE", bg=PANEL, fg=DIM,
                       font=(MONO, 10, "bold"), padx=18, pady=10, cursor="hand2")

    tab_np.pack(side="left")
    tk.Frame(tab_bar, bg=BORDER, width=1).pack(side="left", fill="y", pady=6)
    tab_pre.pack(side="left")

    tab_np.bind("<Button-1>",  lambda _: _show(np_panel,  tab_np,  ACCENT_G, tab_pre))
    tab_pre.bind("<Button-1>", lambda _: _show(pre_panel, tab_pre, ACCENT_B, tab_np))

    # hover effects on tabs
    tab_np.bind("<Enter>",  lambda _: tab_np.configure(fg=ACCENT_G)  if tab_np.cget("fg") != str(ACCENT_G) else None)
    tab_np.bind("<Leave>",  lambda _: None)
    tab_pre.bind("<Enter>", lambda _: tab_pre.configure(fg=TEXT)     if tab_pre.cget("fg") == str(DIM) else None)
    tab_pre.bind("<Leave>", lambda _: tab_pre.configure(fg=DIM)      if tab_pre.cget("fg") == str(TEXT) else None)

    # default: non-preemptive tab active
    np_panel.place(relx=0, rely=0, relwidth=1, relheight=1)
    _active[0] = np_panel

    _h_rule(menu, BORDER)

    # ── status / exit bar ────────────────────────────────
    foot = tk.Frame(menu, bg=PANEL, padx=20, pady=10)
    foot.pack(fill="x", side="bottom")

    tk.Label(foot, text="●  READY", bg=PANEL, fg=ACCENT_G,
             font=(MONO, 8)).pack(side="left")

    exit_btn = tk.Label(foot, text="[ EXIT ]", bg=PANEL, fg=ACCENT_R,
                        font=(MONO, 9, "bold"), padx=8, cursor="hand2")
    exit_btn.pack(side="right")
    exit_btn.bind("<Button-1>", lambda _: menu.destroy())
    exit_btn.bind("<Enter>",    lambda _: exit_btn.configure(bg=ACCENT_R, fg=BG))
    exit_btn.bind("<Leave>",    lambda _: exit_btn.configure(bg=PANEL, fg=ACCENT_R))


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_main_menu()
    root.mainloop()