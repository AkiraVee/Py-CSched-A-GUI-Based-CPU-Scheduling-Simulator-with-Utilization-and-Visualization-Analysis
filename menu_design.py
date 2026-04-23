"""
menu_design.py
==============
Visual design layer for the CPU Scheduling Simulator main menu.

This module centralises every colour, font, and reusable widget builder
used by cpu_scheduler_gui.py so that the look-and-feel can be changed in
one place without touching any algorithm or logic code.

Exports
-------
Colours  : BG, PANEL, BORDER, ACCENT_G, ACCENT_B, ACCENT_R, DIM, TEXT, SUBTEXT
Fonts    : MONO, F_TITLE, F_TAB, F_SECTION, F_ALGO, F_DESC, F_FOOTER, F_VERSION
Helpers  : hex_blend, h_rule
Widgets  : algo_button, build_header, build_tab_bar,
           build_section_header, build_footer
"""

import tkinter as tk
import math


# ═══════════════════════════════════════════════════════════
#  COLOUR PALETTE
#  Single source of truth – change a value here and it
#  propagates to every widget in the application.
# ═══════════════════════════════════════════════════════════
BG       = "#080b10"   # Window / canvas background (near-black)
PANEL    = "#0d1017"   # Card / header / footer background
BORDER   = "#1a2030"   # Dividers and hover-state background
ACCENT_G = "#00ffa3"   # Neon green  – used for Non-Preemptive elements
ACCENT_B = "#00c8ff"   # Neon cyan   – used for Preemptive elements
ACCENT_R = "#ff4d6d"   # Neon red    – used for Exit / danger actions
DIM      = "#2a3245"   # Muted colour for inactive tabs and arrow icons
TEXT     = "#d0d8e8"   # Primary readable text
SUBTEXT  = "#4a5570"   # Secondary / descriptive text
MONO     = "Consolas"  # Monospace font used throughout


# ═══════════════════════════════════════════════════════════
#  FONT SHORTCUTS
#  Defined as tuples so they can be passed directly to the
#  Tkinter `font` parameter.
# ═══════════════════════════════════════════════════════════
F_TITLE   = (MONO, 14, "bold")  # Main window title
F_TAB     = (MONO, 10, "bold")  # Tab switcher labels
F_SECTION = (MONO, 9,  "bold")  # Section header labels
F_ALGO    = (MONO, 11, "bold")  # Algorithm name in each row
F_DESC    = (MONO, 8)           # Descriptor / subtitle text
F_FOOTER  = (MONO, 8)           # Footer status text
F_VERSION = (MONO, 9)           # Version label in header


# ═══════════════════════════════════════════════════════════
#  COLOUR HELPERS
# ═══════════════════════════════════════════════════════════

def hex_blend(base: str, target: str, t: float) -> str:
    """
    Linearly interpolate between two hex colour strings.

    Parameters
    ----------
    base   : str   Starting colour  e.g. "#1a2030"
    target : str   Ending colour    e.g. "#00ffa3"
    t      : float Blend factor 0.0 (all base) → 1.0 (all target)

    Returns
    -------
    str  Resulting hex colour string e.g. "#0d3028"
    """
    br = int(base[1:3], 16);   bg_ = int(base[3:5], 16);   bb = int(base[5:7], 16)
    tr = int(target[1:3], 16); tg  = int(target[3:5], 16); tb = int(target[5:7], 16)
    return (f"#{int(br + (tr - br) * t):02x}"
            f"{int(bg_ + (tg - bg_) * t):02x}"
            f"{int(bb + (tb - bb) * t):02x}")


# ═══════════════════════════════════════════════════════════
#  BASIC WIDGETS
# ═══════════════════════════════════════════════════════════

def h_rule(parent, color=BORDER):
    """
    Pack a single-pixel horizontal divider line onto `parent`.

    Parameters
    ----------
    parent : tk widget  Container to pack the rule into
    color  : str        Line colour (defaults to BORDER)
    """
    tk.Frame(parent, bg=color, height=1).pack(fill="x")


# ═══════════════════════════════════════════════════════════
#  ALGO BUTTON ROW
#  Each algorithm is represented as a clickable row with:
#    • A coloured left stripe matching the category accent
#    • A bold title and a faint descriptor line
#    • A right-side chevron arrow
#    • A sine-wave glow animation that plays while hovered
# ═══════════════════════════════════════════════════════════

def algo_button(parent, label: str, desc: str, command, accent: str):
    """
    Build and pack one algorithm row button.

    The row pulses a blended glow colour on mouse-enter and
    resets cleanly on mouse-leave.  Clicking anywhere on the
    row calls `command`.

    Parameters
    ----------
    parent  : tk widget  Parent container (usually a card Frame)
    label   : str        Algorithm display name  e.g. "Round Robin"
    desc    : str        Short descriptor line   e.g. "RR · Preemptive · ..."
    command : callable   Function to call when the row is clicked
    accent  : str        Hex accent colour for stripe and glow
    """

    # ── outer row frame ───────────────────────────────────
    row = tk.Frame(parent, bg=PANEL, cursor="hand2")
    row.pack(fill="x", padx=0, pady=3)

    # left accent stripe (3 px wide, full row height)
    stripe = tk.Frame(row, bg=accent, width=3)
    stripe.pack(side="left", fill="y")

    # inner content area (title + description)
    inner = tk.Frame(row, bg=PANEL)
    inner.pack(side="left", fill="both", expand=True, padx=16, pady=11)

    # algorithm name – brightens toward accent on hover
    title_lbl = tk.Label(inner, text=label, bg=PANEL, fg=TEXT,
                         font=F_ALGO, anchor="w")
    title_lbl.pack(fill="x")

    # short descriptor line – stays muted
    tk.Label(inner, text=desc, bg=PANEL, fg=SUBTEXT,
             font=F_DESC, anchor="w").pack(fill="x")

    # right-side chevron arrow – lights up on hover
    arrow = tk.Label(row, text="›", bg=PANEL, fg=DIM,
                     font=(MONO, 18), padx=14)
    arrow.pack(side="right")

    # ── recursive widget collector ────────────────────────
    # Needed so we can recolour every child of `row` at once
    def _all(w):
        """Return a flat list of w and all its descendants."""
        out = [w]
        try:
            for c in w.winfo_children():
                out += _all(c)
        except Exception:
            pass
        return out

    # ── glow animation state ──────────────────────────────
    _hovering = [False]   # mutable flag – True while cursor is inside
    _tick     = [0]       # animation frame counter

    def _glow_step():
        """
        Called every 40 ms while the cursor is over the row.
        Uses a sine wave to oscillate the blend factor `t`,
        creating a soft pulsing glow effect.
        """
        if not _hovering[0]:
            return  # stop animating once mouse has left

        # sine-wave blend factor oscillates between ~0.06 and ~0.16
        t = 0.06 + 0.10 * (0.5 + 0.5 * math.sin(_tick[0] * 0.18))

        # blend BORDER → accent for the row background
        glow_bg = hex_blend(BORDER, accent, t)

        # apply glow background to every widget in the row
        for w in _all(row):
            try:
                w.configure(bg=glow_bg)
            except Exception:
                pass

        # stripe brightens toward white
        stripe.configure(bg=hex_blend(accent, "#ffffff", t * 0.45))

        # title text colour shifts toward the accent colour
        title_lbl.configure(fg=hex_blend(TEXT, accent, t * 0.7), bg=glow_bg)

        # arrow turns fully accent-coloured
        arrow.configure(fg=accent, bg=glow_bg)

        _tick[0] += 1
        row.after(40, _glow_step)  # schedule next frame (~25 fps)

    def _enter(_):
        """Mouse entered the row – start the glow animation."""
        _hovering[0] = True
        _tick[0] = 0
        _glow_step()

    def _leave(_):
        """Mouse left the row – stop animation and reset colours."""
        _hovering[0] = False
        for w in _all(row):
            try:
                w.configure(bg=PANEL)
            except Exception:
                pass
        stripe.configure(bg=accent)
        title_lbl.configure(fg=TEXT, bg=PANEL)
        arrow.configure(fg=DIM, bg=PANEL)

    # bind events to every widget in the row
    for w in _all(row):
        w.bind("<Enter>",    _enter)
        w.bind("<Leave>",    _leave)
        w.bind("<Button-1>", lambda _, c=command: c())

    # thin separator below each row
    h_rule(parent, BORDER)


# ═══════════════════════════════════════════════════════════
#  HEADER
#  Top section of the window containing:
#    • A 2 px accent bar at the very top
#    • The application title and version label
#    • A horizontal divider below
# ═══════════════════════════════════════════════════════════

def build_header(parent):
    """
    Build and pack the application header onto `parent`.

    Consists of:
      1. A 2 px ACCENT_G bar at the very top edge
      2. A dark panel row with the title (left) and version (right)
      3. A 1 px horizontal divider below

    Parameters
    ----------
    parent : tk widget  Window or Frame to pack the header into
    """
    # top green accent line
    tk.Frame(parent, bg=ACCENT_G, height=2).pack(fill="x")

    # title row
    hdr = tk.Frame(parent, bg=PANEL, padx=24, pady=16)
    hdr.pack(fill="x")
    tk.Label(hdr, text="◈  CPU SCHEDULING SIMULATOR",
             bg=PANEL, fg=TEXT, font=F_TITLE).pack(side="left")
    tk.Label(hdr, text="v1.0",
             bg=PANEL, fg=SUBTEXT, font=F_VERSION).pack(side="right", pady=4)

    # divider below header
    h_rule(parent, BORDER)


# ═══════════════════════════════════════════════════════════
#  TAB BAR
#  Two-tab switcher for NON-PREEMPTIVE / PREEMPTIVE panels.
#  Handles all switching logic internally so cpu_scheduler_gui
#  only needs to pass the two content panels.
# ═══════════════════════════════════════════════════════════

def build_tab_bar(parent, content_host, np_panel, pre_panel):
    """
    Build and pack the tab switcher bar onto `parent`.

    Clicking a tab shows its corresponding panel and hides the other.
    The active tab is highlighted in its accent colour; the inactive
    tab is dimmed and brightens on hover.

    Parameters
    ----------
    parent       : tk widget  Window to pack the tab bar into
    content_host : tk.Frame   The frame that hosts both panels
    np_panel     : tk.Frame   Non-Preemptive content panel
    pre_panel    : tk.Frame   Preemptive content panel

    Returns
    -------
    (tab_np, tab_pre) : tuple of tk.Label
        The two tab labels, in case the caller needs to reference them.
    """
    tab_bar = tk.Frame(parent, bg=PANEL)
    tab_bar.pack(fill="x")

    # tracks which panel is currently visible
    _active = [None]

    def _show(panel, btn_self, accent, other_btn):
        """Show `panel`, highlight its tab, dim the other tab."""
        panel.place(relx=0, rely=0, relwidth=1, relheight=1)
        if _active[0] and _active[0] is not panel:
            _active[0].place_forget()
        _active[0] = panel
        btn_self.configure(fg=accent, bg=BG)    # active tab: accent colour on dark bg
        other_btn.configure(fg=DIM, bg=PANEL)   # inactive tab: dimmed on panel bg

    # NON-PREEMPTIVE tab label (starts active/green)
    tab_np = tk.Label(tab_bar, text="NON-PREEMPTIVE", bg=PANEL, fg=ACCENT_G,
                      font=F_TAB, padx=18, pady=10, cursor="hand2")

    # PREEMPTIVE tab label (starts inactive/dimmed)
    tab_pre = tk.Label(tab_bar, text="PREEMPTIVE", bg=PANEL, fg=DIM,
                       font=F_TAB, padx=18, pady=10, cursor="hand2")

    tab_np.pack(side="left")
    # thin vertical divider between the two tabs
    tk.Frame(tab_bar, bg=BORDER, width=1).pack(side="left", fill="y", pady=6)
    tab_pre.pack(side="left")

    # click bindings – switch panels on click
    tab_np.bind("<Button-1>",  lambda _: _show(np_panel,  tab_np,  ACCENT_G, tab_pre))
    tab_pre.bind("<Button-1>", lambda _: _show(pre_panel, tab_pre, ACCENT_B, tab_np))

    # hover bindings – subtle highlight on inactive tab
    tab_np.bind("<Enter>",  lambda _: tab_np.configure(fg=ACCENT_G)
                            if tab_np.cget("fg") != str(ACCENT_G) else None)
    tab_pre.bind("<Enter>", lambda _: tab_pre.configure(fg=TEXT)
                            if tab_pre.cget("fg") == str(DIM) else None)
    tab_pre.bind("<Leave>", lambda _: tab_pre.configure(fg=DIM)
                            if tab_pre.cget("fg") == str(TEXT) else None)

    # show NON-PREEMPTIVE panel by default on open
    np_panel.place(relx=0, rely=0, relwidth=1, relheight=1)
    _active[0] = np_panel

    return tab_np, tab_pre


# ═══════════════════════════════════════════════════════════
#  SECTION HEADER
#  Coloured label placed above the algorithm card inside
#  each panel, with a faint subtitle on the right side.
# ═══════════════════════════════════════════════════════════

def build_section_header(parent, title: str, subtitle: str, accent: str):
    """
    Build and pack a section header row onto `parent`.

    Parameters
    ----------
    parent   : tk widget  Panel frame to pack into
    title    : str        Bold section label  e.g. "NON-PREEMPTIVE ALGORITHMS"
    subtitle : str        Faint right-side note  e.g. "process runs to completion"
    accent   : str        Hex colour for the title text
    """
    row = tk.Frame(parent, bg=BG, padx=24, pady=14)
    row.pack(fill="x")
    tk.Label(row, text=title,    bg=BG, fg=accent,  font=F_SECTION).pack(side="left")
    tk.Label(row, text=subtitle, bg=BG, fg=SUBTEXT, font=F_DESC).pack(side="right")
    h_rule(parent, BORDER)


# ═══════════════════════════════════════════════════════════
#  FOOTER
#  Bottom bar containing:
#    • A green "● READY" status indicator on the left
#    • A red "[ EXIT ]" button on the right that
#      inverts colours on hover
# ═══════════════════════════════════════════════════════════

def build_footer(parent, on_exit):
    """
    Build and pack the footer bar onto `parent`.

    Parameters
    ----------
    parent   : tk widget  Window to pack the footer into
    on_exit  : callable   Called when the EXIT button is clicked
    """
    # top divider above footer
    h_rule(parent, BORDER)

    foot = tk.Frame(parent, bg=PANEL, padx=20, pady=10)
    foot.pack(fill="x", side="bottom")

    # status indicator on the left
    tk.Label(foot, text="●  READY", bg=PANEL, fg=ACCENT_G,
             font=F_FOOTER).pack(side="left")

    # EXIT button on the right – inverts bg/fg on hover
    exit_btn = tk.Label(foot, text="[ EXIT ]", bg=PANEL, fg=ACCENT_R,
                        font=(MONO, 9, "bold"), padx=8, cursor="hand2")
    exit_btn.pack(side="right")
    exit_btn.bind("<Button-1>", lambda _: on_exit())
    exit_btn.bind("<Enter>",    lambda _: exit_btn.configure(bg=ACCENT_R, fg=BG))
    exit_btn.bind("<Leave>",    lambda _: exit_btn.configure(bg=PANEL,    fg=ACCENT_R))