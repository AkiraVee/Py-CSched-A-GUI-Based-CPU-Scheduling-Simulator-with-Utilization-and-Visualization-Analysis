"""
theme.py
========
Shared UI toolkit for the CPU Scheduling Simulator algorithm windows.

Every algorithm file imports from here to ensure a consistent look
across all windows.  Only this file needs to change if the visual
style is updated.

Usage
-----
    from theme import (
        AlgoWindow, Widgets, Output,
        section_header, h_rule,
        ACCENT_G, ACCENT_B, ACCENT_R, ...
    )

    def my_algo_gui():
        win = AlgoWindow("My Algorithm", accent=ACCENT_G)
        # build input widgets on win.body
        # write results via Output(Widgets.output_box(win.body))
        win.grab_set()
"""

import tkinter as tk
import math


# ═══════════════════════════════════════════════════════════
#  PALETTE  (matches menu_design.py)
# ═══════════════════════════════════════════════════════════
BG        = "#080b10"   # Window background
PANEL     = "#0d1017"   # Header / footer panel
SIDEBAR   = "#0a0d14"   # (reserved for future use)
BORDER    = "#1a2030"   # Dividers and borders
CARD      = "#111520"   # Input row alternating background
ACCENT_G  = "#00ffa3"   # Neon green  – Non-Preemptive algorithms
ACCENT_B  = "#00c8ff"   # Neon cyan   – Preemptive algorithms
ACCENT_R  = "#ff4d6d"   # Neon red    – Danger / Close / Clear
ACCENT_Y  = "#ffd166"   # Amber       – Warnings
DIM       = "#2a3245"   # Muted / inactive elements
TEXT      = "#d0d8e8"   # Primary text
SUBTEXT   = "#4a5570"   # Secondary / hint text
SUCCESS   = ACCENT_G    # Alias used for success states
MONO      = "Consolas"  # Monospace font

# ── font shortcuts ────────────────────────────────────────
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
#  Identical to the one in menu_design so algorithm windows
#  share the same header animation style.
# ═══════════════════════════════════════════════════════════

class GlowBar(tk.Canvas):
    """
    A 6 px tall Canvas at the top of each algorithm window.
    Pulses its brightness using a sine wave at ~20 fps.
    """

    def __init__(self, parent, color=ACCENT_G, **kw):
        super().__init__(parent, height=6, bd=0,
                         highlightthickness=0, bg=BG, **kw)
        self._color = color
        self._tick  = 0
        self._pulse()

    def _hex_brightness(self, t):
        """Scale each RGB channel of self._color by factor t (0–1)."""
        r = int(int(self._color[1:3], 16) * t)
        g = int(int(self._color[3:5], 16) * t)
        b = int(int(self._color[5:7], 16) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _pulse(self):
        """Redraw the bar at each animation frame."""
        self.delete("all")
        try:    w = self.winfo_width() or 800
        except: w = 800

        # brightness oscillates between 0.45 and 1.0
        t   = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(self._tick * 0.12))
        col = self._hex_brightness(t)

        # main bright bar
        self.create_rectangle(0, 0, w, 6,  fill=col, outline="")
        # soft glow bleed below the bar
        self.create_rectangle(0, 6, w, 14, fill=self._hex_brightness(t * 0.22), outline="")

        self._tick += 1
        self.after(50, self._pulse)  # ~20 fps


# ═══════════════════════════════════════════════════════════
#  LAYOUT HELPERS
# ═══════════════════════════════════════════════════════════

def h_rule(parent, color=BORDER):
    """Pack a 1 px horizontal divider line onto parent."""
    tk.Frame(parent, bg=color, height=1).pack(fill="x")


def section_header(parent, title: str, subtitle: str = "", accent=ACCENT_G):
    """
    Pack a coloured section label + optional right-side subtitle.

    Parameters
    ----------
    parent   : tk widget  Parent to pack into
    title    : str        Bold section text  e.g. "STEP 1 – PROCESS COUNT"
    subtitle : str        Faint right-side hint (optional)
    accent   : str        Hex colour for the title
    """
    row = tk.Frame(parent, bg=BG, padx=20, pady=12)
    row.pack(fill="x")
    tk.Label(row, text=title,    bg=BG, fg=accent,  font=F_SECTION).pack(side="left")
    if subtitle:
        tk.Label(row, text=subtitle, bg=BG, fg=SUBTEXT, font=F_SMALL).pack(side="right")
    h_rule(parent, BORDER)


# ═══════════════════════════════════════════════════════════
#  WIDGETS  – factory helpers for algorithm input forms
# ═══════════════════════════════════════════════════════════

class Widgets:
    """Collection of static factory methods for styled Tkinter widgets."""

    @staticmethod
    def labelled_entry(parent, label: str, accent=ACCENT_G, width=8):
        """
        Build a label + entry field pair in a row frame.

        Returns (row_frame, tk.Entry).  Caller is responsible for packing row_frame.
        """
        row = tk.Frame(parent, bg=CARD, pady=0)
        tk.Label(row, text=label, bg=CARD, fg=SUBTEXT,
                 font=F_LABEL, width=22, anchor="w").pack(side="left", padx=(14, 4), pady=8)
        entry = tk.Entry(row, bg=BORDER, fg=TEXT,
                         insertbackground=accent,
                         relief="flat", font=F_INPUT, width=width,
                         highlightthickness=1,
                         highlightcolor=accent,
                         highlightbackground=BORDER)
        entry.pack(side="left", padx=(0, 14), pady=8)
        return row, entry

    @staticmethod
    def button(parent, text: str, command, accent=ACCENT_G, width=18):
        """
        Build a flat styled button with hover highlight.

        Returns the tk.Button (not yet packed).
        """
        btn = tk.Button(parent, text=text, command=command,
                        bg=CARD, fg=accent,
                        activebackground=BORDER, activeforeground=accent,
                        relief="flat", font=(MONO, 10, "bold"),
                        width=width, pady=8, cursor="hand2",
                        bd=0, highlightthickness=1,
                        highlightbackground=DIM, highlightcolor=accent)
        btn.bind("<Enter>", lambda _: btn.configure(bg=BORDER, highlightbackground=accent))
        btn.bind("<Leave>", lambda _: btn.configure(bg=CARD,   highlightbackground=DIM))
        return btn

    @staticmethod
    def output_box(parent, height=18, accent=ACCENT_G):
        """
        Build a read-only monospace output text box with a vertical scrollbar.

        Pre-configured colour tags:
          "accent"  – accent colour text
          "success" – green text
          "warn"    – amber text
          "error"   – red text
          "dim"     – muted text
          "header"  – bold accent text (used for section titles)
          "bold"    – bold white text (used for table headers)

        Returns the tk.Text widget.
        """
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

        # configure named colour tags for rich output formatting
        text.tag_configure("accent",  foreground=accent)
        text.tag_configure("success", foreground=ACCENT_G)
        text.tag_configure("warn",    foreground=ACCENT_Y)
        text.tag_configure("error",   foreground=ACCENT_R)
        text.tag_configure("dim",     foreground=SUBTEXT)
        text.tag_configure("header",  foreground=accent, font=(MONO, 9, "bold"))
        text.tag_configure("bold",    font=(MONO, 9, "bold"), foreground=TEXT)

        return text

    @staticmethod
    def count_bar(parent, label="Process count", accent=ACCENT_G):
        """
        Build a compact single-row process-count input bar.

        Returns (bar_frame, tk.Entry).  Caller packs bar_frame.
        CONFIRM button should be added by the caller after this.
        """
        bar = tk.Frame(parent, bg=PANEL, padx=16, pady=10)
        tk.Label(bar, text=label, bg=PANEL, fg=SUBTEXT, font=F_LABEL).pack(side="left")
        e = tk.Entry(bar, bg=BORDER, fg=TEXT,
                     insertbackground=accent,
                     relief="flat", font=F_INPUT, width=5,
                     highlightthickness=1,
                     highlightcolor=accent,
                     highlightbackground=BORDER)
        e.pack(side="left", padx=10)
        return bar, e

    @staticmethod
    def chip(parent, text: str, accent=ACCENT_G):
        """Build a small pill-shaped label badge. Returns the tk.Label."""
        return tk.Label(parent, text=f" {text} ", bg=DIM, fg=accent,
                        font=(MONO, 8, "bold"), padx=4)

    @staticmethod
    def divider(parent, color=BORDER):
        """Pack a 1 px divider with side padding inside a body frame."""
        tk.Frame(parent, bg=color, height=1).pack(fill="x", padx=16, pady=4)

    @staticmethod
    def error(parent, msg: str):
        """
        Display a modal error popup over `parent`.

        Parameters
        ----------
        parent : tk widget  Used as the popup's parent for centering
        msg    : str        Error message text to display
        """
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
#  ALGO WINDOW  – base Toplevel for every algorithm
# ═══════════════════════════════════════════════════════════

class AlgoWindow(tk.Toplevel):
    """
    Pre-built Toplevel window used by every algorithm GUI.

    Provides:
      • GlowBar animated accent line at the top
      • Styled header with algorithm title and category chip
      • Scrollable body frame (self.body) for input widgets
      • Pulsing status dot in the footer
      • [ CLOSE ] button in the footer

    Usage
    -----
        win = AlgoWindow("FCFS – First Come First Serve", accent=ACCENT_G)
        # place input / output widgets on win.body
        win.set_status("Running…")   # update footer text
        win.grab_set()               # make window modal
    """

    def __init__(self, title: str, accent=ACCENT_G, width=780, height=620):
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(True, True)
        self.configure(bg=BG)
        self._accent = accent

        # ── animated glow bar ─────────────────────────────
        GlowBar(self, color=accent).pack(fill="x")

        # ── header row ────────────────────────────────────
        hdr = tk.Frame(self, bg=PANEL, padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, bg=PANEL, fg=TEXT, font=F_TITLE).pack(side="left")
        # category chip (NON-PREEMPTIVE or PREEMPTIVE)
        chip_text = "NON-PREEMPTIVE" if accent == ACCENT_G else "PREEMPTIVE"
        Widgets.chip(hdr, chip_text, accent).pack(side="right", pady=2)

        h_rule(self, BORDER)

        # ── scrollable body ───────────────────────────────
        # Canvas + Scrollbar so long input forms can scroll
        outer  = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=BG, bd=0, highlightthickness=0)
        scroll = tk.Scrollbar(outer, orient="vertical",
                              command=canvas.yview,
                              bg=PANEL, troughcolor=CARD,
                              activebackground=accent)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left",  fill="both", expand=True)

        # self.body is where all algorithm content is placed
        self.body = tk.Frame(canvas, bg=BG)
        _win_id   = canvas.create_window((0, 0), window=self.body, anchor="nw")

        def _resize(e):
            """Keep scrollregion and window width in sync with canvas."""
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(_win_id, width=canvas.winfo_width())

        self.body.bind("<Configure>", _resize)
        canvas.bind("<Configure>",    _resize)

        # mouse wheel scrolling
        def _scroll(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        self.body.bind_all("<MouseWheel>", _scroll)

        # ── footer ────────────────────────────────────────
        h_rule(self, BORDER)
        foot = tk.Frame(self, bg=PANEL, padx=16, pady=8)
        foot.pack(fill="x", side="bottom")

        self._status_dot = tk.Label(foot, text="●", bg=PANEL, fg=accent, font=(MONO, 9))
        self._status_dot.pack(side="left")
        self._status_lbl = tk.Label(foot, text="  READY", bg=PANEL, fg=SUBTEXT, font=F_SMALL)
        self._status_lbl.pack(side="left")

        # CLOSE button – destroys only this window
        close_btn = tk.Label(foot, text="[ CLOSE ]", bg=PANEL, fg=ACCENT_R,
                             font=(MONO, 9, "bold"), padx=8, cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda _: self.destroy())
        close_btn.bind("<Enter>",    lambda _: close_btn.configure(bg=ACCENT_R, fg=BG))
        close_btn.bind("<Leave>",    lambda _: close_btn.configure(bg=PANEL,    fg=ACCENT_R))

        # start the footer dot pulse animation
        self._dot_tick   = 0
        self._dot_bright = [accent, accent, DIM, DIM]
        self._pulse_dot()

    def _pulse_dot(self):
        """Cycle the status dot through brightness levels every 700 ms."""
        try:
            self._status_dot.configure(fg=self._dot_bright[self._dot_tick % 4])
            self._dot_tick += 1
            self.after(700, self._pulse_dot)
        except Exception:
            pass  # window was destroyed – stop silently

    def set_status(self, msg: str, color=None):
        """
        Update the footer status label text and optional colour.

        Parameters
        ----------
        msg   : str  Status text  e.g. "Simulation complete"
        color : str  Optional hex colour override (defaults to SUBTEXT)
        """
        self._status_lbl.configure(text=f"  {msg}", fg=color or SUBTEXT)


# ═══════════════════════════════════════════════════════════
#  OUTPUT  – structured writer for the output text box
# ═══════════════════════════════════════════════════════════

class Output:
    """
    Thin wrapper around a tk.Text widget for structured terminal-style output.

    All text is appended at the end.  The widget is kept in DISABLED
    state between writes to prevent user edits.

    Named colour tags (defined in Widgets.output_box):
      "accent"  "success"  "warn"  "error"  "dim"  "header"  "bold"

    Example
    -------
        out = Output(Widgets.output_box(win.body, accent=ACCENT_G))
        out.line("GANTT CHART:", tag="header")
        out.line("| P1 | P2 |",  tag="accent")
        out.divider()
        out.kv("CPU Utilization (%)", "95.00")
    """

    def __init__(self, text_widget: tk.Text):
        self._t = text_widget

    def clear(self):
        """Erase all content from the output box."""
        self._t.configure(state="normal")
        self._t.delete("1.0", "end")
        # leave disabled until next write

    def line(self, text="", tag=None, end="\n"):
        """
        Append one line of text.

        Parameters
        ----------
        text : str        The text to write
        tag  : str|None   Named colour tag, or None for default TEXT colour
        end  : str        Line ending (default newline)
        """
        self._t.configure(state="normal")
        if tag:
            self._t.insert("end", text + end, tag)
        else:
            self._t.insert("end", text + end)
        self._t.configure(state="disabled")
        self._t.see("end")  # auto-scroll to bottom

    def divider(self, char="─", length=72, tag="dim"):
        """Append a horizontal divider line."""
        self.line(char * length, tag=tag)

    def blank(self):
        """Append an empty line."""
        self.line("")

    def table_row(self, *cols, widths, tag=None):
        """
        Append a fixed-width table row.

        Parameters
        ----------
        *cols  : values   Column values (converted to str and left-justified)
        widths : list     Column widths in characters
        tag    : str|None Colour tag for the entire row
        """
        row = "".join(str(c).ljust(w) for c, w in zip(cols, widths))
        self.line(row, tag=tag)

    def kv(self, key: str, value, accent_tag="accent"):
        """
        Append a key: value pair with the key in dim and value in accent.

        Parameters
        ----------
        key        : str  Label e.g. "CPU Utilization (%)"
        value      : any  The value to display (converted to str)
        accent_tag : str  Tag for the value (default "accent")
        """
        self._t.configure(state="normal")
        self._t.insert("end", f"  {key:<28}", "dim")
        self._t.insert("end", str(value) + "\n", accent_tag)
        self._t.configure(state="disabled")