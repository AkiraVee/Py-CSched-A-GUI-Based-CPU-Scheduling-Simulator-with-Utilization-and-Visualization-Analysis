"""
theme.py  –  Shared UI toolkit for CPU Scheduling Simulator
============================================================
Import this in every algorithm file:

    from theme import *          # colours, fonts
    from theme import AlgoWindow # main window builder
    from theme import Widgets    # helper widget factory

Usage example (in fcfs_algorithm.py):
    def fcfs_gui():
        win = AlgoWindow("FCFS – First Come First Serve", ACCENT_G)
        # ... build your input form with Widgets helpers ...
        win.mainloop()
"""

import tkinter as tk
import math


# ═══════════════════════════════════════════════════════════
#  PALETTE  (single source of truth – matches main menu)
# ═══════════════════════════════════════════════════════════
BG        = "#080b10"
PANEL     = "#0d1017"
SIDEBAR   = "#0a0d14"
BORDER    = "#1a2030"
CARD      = "#111520"
ACCENT_G  = "#00ffa3"   # Non-Preemptive
ACCENT_B  = "#00c8ff"   # Preemptive
ACCENT_R  = "#ff4d6d"   # danger / exit
ACCENT_Y  = "#ffd166"   # warning / highlight
DIM       = "#2a3245"
TEXT      = "#d0d8e8"
SUBTEXT   = "#4a5570"
SUCCESS   = ACCENT_G
MONO      = "Consolas"

# Font shortcuts
F_TITLE   = (MONO, 13, "bold")
F_SECTION = (MONO, 9,  "bold")
F_BODY    = (MONO, 11)
F_SMALL   = (MONO, 8)
F_LABEL   = (MONO, 10)
F_INPUT   = (MONO, 11)
F_TABLE   = (MONO, 10)
F_CODE    = (MONO, 9)


# ═══════════════════════════════════════════════════════════
#  ANIMATED GLOW BAR
# ═══════════════════════════════════════════════════════════
class GlowBar(tk.Canvas):
    """Pulsing 6-px accent line (same as main menu)."""

    def __init__(self, parent, color=ACCENT_G, **kw):
        super().__init__(parent, height=6, bd=0,
                         highlightthickness=0, bg=BG, **kw)
        self._color = color
        self._tick  = 0
        self._pulse()

    def _hex_brightness(self, t):
        r = int(int(self._color[1:3], 16) * t)
        g = int(int(self._color[3:5], 16) * t)
        b = int(int(self._color[5:7], 16) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _pulse(self):
        self.delete("all")
        try:
            w = self.winfo_width() or 800
        except Exception:
            w = 800
        t   = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(self._tick * 0.12))
        col = self._hex_brightness(t)
        self.create_rectangle(0, 0, w, 6,  fill=col, outline="")
        glow = self._hex_brightness(t * 0.22)
        self.create_rectangle(0, 6, w, 14, fill=glow, outline="")
        self._tick += 1
        self.after(50, self._pulse)


# ═══════════════════════════════════════════════════════════
#  SECTION HEADER HELPER
# ═══════════════════════════════════════════════════════════
def h_rule(parent, color=BORDER):
    tk.Frame(parent, bg=color, height=1).pack(fill="x")


def section_header(parent, title, subtitle="", accent=ACCENT_G):
    """Coloured section label + faint subtitle on the right."""
    row = tk.Frame(parent, bg=BG, padx=20, pady=12)
    row.pack(fill="x")
    tk.Label(row, text=title, bg=BG, fg=accent,
             font=F_SECTION).pack(side="left")
    if subtitle:
        tk.Label(row, text=subtitle, bg=BG, fg=SUBTEXT,
                 font=F_SMALL).pack(side="right")
    h_rule(parent, BORDER)


# ═══════════════════════════════════════════════════════════
#  WIDGETS  – factory helpers used inside algorithm windows
# ═══════════════════════════════════════════════════════════
class Widgets:

    # ── labelled entry ──────────────────────────────────────
    @staticmethod
    def labelled_entry(parent, label, accent=ACCENT_G, width=8):
        """Returns (row_frame, tk.Entry).  Caller packs the row."""
        row = tk.Frame(parent, bg=CARD, pady=0)

        tk.Label(row, text=label, bg=CARD, fg=SUBTEXT,
                 font=F_LABEL, width=22, anchor="w").pack(side="left", padx=(14, 4), pady=8)

        entry = tk.Entry(row, bg=BORDER, fg=TEXT, insertbackground=accent,
                         relief="flat", font=F_INPUT, width=width,
                         highlightthickness=1, highlightcolor=accent,
                         highlightbackground=BORDER)
        entry.pack(side="left", padx=(0, 14), pady=8)

        return row, entry

    # ── styled button ───────────────────────────────────────
    @staticmethod
    def button(parent, text, command, accent=ACCENT_G, width=18):
        btn = tk.Button(parent, text=text, command=command,
                        bg=CARD, fg=accent,
                        activebackground=BORDER, activeforeground=accent,
                        relief="flat", font=(MONO, 10, "bold"),
                        width=width, pady=8, cursor="hand2",
                        bd=0, highlightthickness=1,
                        highlightbackground=DIM,
                        highlightcolor=accent)
        btn.bind("<Enter>", lambda _: btn.configure(bg=BORDER, highlightbackground=accent))
        btn.bind("<Leave>", lambda _: btn.configure(bg=CARD,   highlightbackground=DIM))
        return btn

    # ── read-only output text box ────────────────────────────
    @staticmethod
    def output_box(parent, height=18, accent=ACCENT_G):
        """Returns a tk.Text widget pre-styled for monospace output."""
        frame = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        frame.pack(fill="both", expand=True, padx=16, pady=(8, 12))

        text = tk.Text(frame, bg=CARD, fg=TEXT,
                       insertbackground=accent,
                       relief="flat", font=F_CODE,
                       height=height, wrap="none",
                       selectbackground=BORDER,
                       selectforeground=accent)
        text.pack(side="left", fill="both", expand=True)

        scroll_y = tk.Scrollbar(frame, orient="vertical",
                                command=text.yview,
                                bg=PANEL, troughcolor=CARD,
                                activebackground=accent)
        scroll_y.pack(side="right", fill="y")
        text.configure(yscrollcommand=scroll_y.set)

        # colour tags for rich output
        text.tag_configure("accent",  foreground=accent)
        text.tag_configure("success", foreground=ACCENT_G)
        text.tag_configure("warn",    foreground=ACCENT_Y)
        text.tag_configure("error",   foreground=ACCENT_R)
        text.tag_configure("dim",     foreground=SUBTEXT)
        text.tag_configure("header",  foreground=accent, font=(MONO, 9, "bold"))
        text.tag_configure("bold",    font=(MONO, 9, "bold"), foreground=TEXT)

        return text

    # ── process-count entry bar ─────────────────────────────
    @staticmethod
    def count_bar(parent, label="Process count", accent=ACCENT_G):
        """Returns (frame, entry).  Compact single-row count input."""
        bar = tk.Frame(parent, bg=PANEL, padx=16, pady=10)
        tk.Label(bar, text=label, bg=PANEL, fg=SUBTEXT,
                 font=F_LABEL).pack(side="left")
        e = tk.Entry(bar, bg=BORDER, fg=TEXT, insertbackground=accent,
                     relief="flat", font=F_INPUT, width=5,
                     highlightthickness=1, highlightcolor=accent,
                     highlightbackground=BORDER)
        e.pack(side="left", padx=10)
        return bar, e

    # ── info chip (small pill label) ────────────────────────
    @staticmethod
    def chip(parent, text, accent=ACCENT_G):
        return tk.Label(parent, text=f" {text} ", bg=DIM, fg=accent,
                        font=(MONO, 8, "bold"), padx=4)

    # ── divider ─────────────────────────────────────────────
    @staticmethod
    def divider(parent, color=BORDER):
        tk.Frame(parent, bg=color, height=1).pack(fill="x", padx=16, pady=4)

    # ── error popup ─────────────────────────────────────────
    @staticmethod
    def error(parent, msg):
        popup = tk.Toplevel(parent)
        popup.title("Error")
        popup.configure(bg=BG)
        popup.resizable(False, False)
        tk.Frame(popup, bg=ACCENT_R, height=3).pack(fill="x")
        tk.Label(popup, text="⚠  " + msg, bg=BG, fg=ACCENT_R,
                 font=F_BODY, padx=24, pady=20).pack()
        Widgets.button(popup, "OK", popup.destroy,
                       accent=ACCENT_R, width=12).pack(pady=(0, 16))
        popup.grab_set()


# ═══════════════════════════════════════════════════════════
#  ALGO WINDOW  – base Toplevel every algorithm opens
# ═══════════════════════════════════════════════════════════
class AlgoWindow(tk.Toplevel):
    """
    Pre-built Toplevel with:
      • animated glow bar
      • styled header (title + accent chip)
      • scrollable main body
      • footer with status dot

    Usage:
        win = AlgoWindow("FCFS – First Come First Serve", accent=ACCENT_G)
        # place widgets inside  win.body
        # call win.set_status("Running…") to update footer
    """

    def __init__(self, title, accent=ACCENT_G, width=780, height=620):
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(True, True)
        self.configure(bg=BG)
        self._accent = accent

        # ── glow bar ──────────────────────────────────
        GlowBar(self, color=accent).pack(fill="x")

        # ── header ────────────────────────────────────
        hdr = tk.Frame(self, bg=PANEL, padx=20, pady=14)
        hdr.pack(fill="x")

        tk.Label(hdr, text=title, bg=PANEL, fg=TEXT,
                 font=F_TITLE).pack(side="left")

        chip = Widgets.chip(hdr, "NON-PREEMPTIVE" if accent == ACCENT_G else "PREEMPTIVE",
                            accent)
        chip.pack(side="right", pady=2)

        h_rule(self, BORDER)

        # ── scrollable body ───────────────────────────
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=BG, bd=0,
                           highlightthickness=0)
        scroll = tk.Scrollbar(outer, orient="vertical",
                              command=canvas.yview,
                              bg=PANEL, troughcolor=CARD,
                              activebackground=accent)
        canvas.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.body = tk.Frame(canvas, bg=BG)
        _win_id = canvas.create_window((0, 0), window=self.body, anchor="nw")

        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(_win_id, width=canvas.winfo_width())

        self.body.bind("<Configure>", _resize)
        canvas.bind("<Configure>",    _resize)

        # mousewheel scroll
        def _scroll(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        self.body.bind_all("<MouseWheel>", _scroll)

        # ── footer ────────────────────────────────────
        h_rule(self, BORDER)
        foot = tk.Frame(self, bg=PANEL, padx=16, pady=8)
        foot.pack(fill="x", side="bottom")

        self._status_dot = tk.Label(foot, text="●", bg=PANEL, fg=accent,
                                    font=(MONO, 9))
        self._status_dot.pack(side="left")
        self._status_lbl = tk.Label(foot, text="  READY", bg=PANEL, fg=SUBTEXT,
                                    font=F_SMALL)
        self._status_lbl.pack(side="left")

        close_btn = tk.Label(foot, text="[ CLOSE ]", bg=PANEL, fg=ACCENT_R,
                             font=(MONO, 9, "bold"), padx=8, cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda _: self.destroy())
        close_btn.bind("<Enter>",    lambda _: close_btn.configure(bg=ACCENT_R, fg=BG))
        close_btn.bind("<Leave>",    lambda _: close_btn.configure(bg=PANEL,    fg=ACCENT_R))

        self._dot_tick = 0
        self._dot_bright = [accent, accent, DIM, DIM]
        self._pulse_dot()

    def _pulse_dot(self):
        try:
            self._status_dot.configure(
                fg=self._dot_bright[self._dot_tick % 4])
            self._dot_tick += 1
            self.after(700, self._pulse_dot)
        except Exception:
            pass

    def set_status(self, msg, color=None):
        """Update footer status text."""
        self._status_lbl.configure(text=f"  {msg}",
                                   fg=color or SUBTEXT)


# ═══════════════════════════════════════════════════════════
#  OUTPUT HELPERS  – write formatted text into an output_box
# ═══════════════════════════════════════════════════════════
class Output:
    """
    Thin wrapper around a tk.Text widget for structured terminal output.

    Usage:
        out = Output(text_widget)
        out.line("GANTT CHART:", tag="header")
        out.line("| P1 | P2 |")
        out.divider()
    """

    def __init__(self, text_widget: tk.Text):
        self._t = text_widget

    def clear(self):
        self._t.configure(state="normal")
        self._t.delete("1.0", "end")

    def line(self, text="", tag=None, end="\n"):
        self._t.configure(state="normal")
        if tag:
            self._t.insert("end", text + end, tag)
        else:
            self._t.insert("end", text + end)
        self._t.configure(state="disabled")
        self._t.see("end")

    def divider(self, char="─", length=72, tag="dim"):
        self.line(char * length, tag=tag)

    def blank(self):
        self.line("")

    def table_row(self, *cols, widths, tag=None):
        """Print a fixed-width table row."""
        row = "".join(str(c).ljust(w) for c, w in zip(cols, widths))
        self.line(row, tag=tag)

    def kv(self, key, value, accent_tag="accent"):
        """Print a key: value pair."""
        self._t.configure(state="normal")
        self._t.insert("end", f"  {key:<28}", "dim")
        self._t.insert("end", str(value) + "\n", accent_tag)
        self._t.configure(state="disabled")