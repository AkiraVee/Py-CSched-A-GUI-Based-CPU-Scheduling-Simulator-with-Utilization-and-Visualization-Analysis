import tkinter as tk
from tkinter import ttk
import math

BG       = "#080b10"
PANEL    = "#0d1017"
BORDER   = "#1a2030"
ACCENT_G = "#00ffa3"
ACCENT_B = "#00c8ff"
ACCENT_R = "#ff4d6d"
DIM      = "#2a3245"
TEXT     = "#d0d8e8"
SUBTEXT  = "#4a5570"
MONO     = "Consolas"

F_TITLE   = (MONO, 14, "bold")
F_TAB     = (MONO, 10, "bold")
F_SECTION = (MONO, 9,  "bold")
F_ALGO    = (MONO, 11, "bold")
F_DESC    = (MONO, 8)
F_FOOTER  = (MONO, 8)
F_VERSION = (MONO, 9)


def hex_blend(base: str, target: str, t: float) -> str:
    br = int(base[1:3], 16);   bg_ = int(base[3:5], 16);   bb = int(base[5:7], 16)
    tr = int(target[1:3], 16); tg  = int(target[3:5], 16); tb = int(target[5:7], 16)
    return (f"#{int(br + (tr - br) * t):02x}"
            f"{int(bg_ + (tg - bg_) * t):02x}"
            f"{int(bb + (tb - bb) * t):02x}")


def h_rule(parent, color=BORDER):
    tk.Frame(parent, bg=color, height=1).pack(fill="x")


def algo_button(parent, label: str, desc: str, command, accent: str):
    row = tk.Frame(parent, bg=PANEL, cursor="hand2")
    row.pack(fill="x", padx=0, pady=3)

    stripe = tk.Frame(row, bg=accent, width=3)
    stripe.pack(side="left", fill="y")

    inner = tk.Frame(row, bg=PANEL)
    inner.pack(side="left", fill="both", expand=True, padx=16, pady=11)

    title_lbl = tk.Label(inner, text=label, bg=PANEL, fg=TEXT,
                         font=F_ALGO, anchor="w")
    title_lbl.pack(fill="x")

    tk.Label(inner, text=desc, bg=PANEL, fg=SUBTEXT,
             font=F_DESC, anchor="w").pack(fill="x")

    arrow = tk.Label(row, text="›", bg=PANEL, fg=DIM,
                     font=(MONO, 18), padx=14)
    arrow.pack(side="right")

    def _all(w):
        out = [w]
        try:
            for c in w.winfo_children(): out += _all(c)
        except Exception: pass
        return out

    _hovering = [False]
    _tick     = [0]

    def _glow_step():
        if not _hovering[0]:
            return
        t = 0.06 + 0.10 * (0.5 + 0.5 * math.sin(_tick[0] * 0.18))
        glow_bg = hex_blend(BORDER, accent, t)
        for w in _all(row):
            try: w.configure(bg=glow_bg)
            except Exception: pass
        stripe.configure(bg=hex_blend(accent, "#ffffff", t * 0.45))
        title_lbl.configure(fg=hex_blend(TEXT, accent, t * 0.7), bg=glow_bg)
        arrow.configure(fg=accent, bg=glow_bg)
        _tick[0] += 1
        row.after(40, _glow_step)

    def _enter(_):
        _hovering[0] = True
        _tick[0] = 0
        _glow_step()

    def _leave(_):
        _hovering[0] = False
        for w in _all(row):
            try: w.configure(bg=PANEL)
            except Exception: pass
        stripe.configure(bg=accent)
        title_lbl.configure(fg=TEXT, bg=PANEL)
        arrow.configure(fg=DIM, bg=PANEL)

    for w in _all(row):
        w.bind("<Enter>",    _enter)
        w.bind("<Leave>",    _leave)
        w.bind("<Button-1>", lambda _, c=command: c())

    h_rule(parent, BORDER)


def build_header(parent):
    tk.Frame(parent, bg=ACCENT_G, height=2).pack(fill="x")
    hdr = tk.Frame(parent, bg=PANEL, padx=24, pady=16)
    hdr.pack(fill="x")
    tk.Label(hdr, text="◈  CPU SCHEDULING SIMULATOR",
             bg=PANEL, fg=TEXT, font=F_TITLE).pack(side="left")
    tk.Label(hdr, text="v1.0",
             bg=PANEL, fg=SUBTEXT, font=F_VERSION).pack(side="right", pady=4)
    h_rule(parent, BORDER)


def build_tab_bar(parent, content_host, np_panel, pre_panel):
    tab_bar = tk.Frame(parent, bg=PANEL)
    tab_bar.pack(fill="x")

    _active = [None]

    def _show(panel, btn_self, accent, other_btn):
        panel.place(relx=0, rely=0, relwidth=1, relheight=1)
        if _active[0] and _active[0] is not panel:
            _active[0].place_forget()
        _active[0] = panel
        btn_self.configure(fg=accent, bg=BG)
        other_btn.configure(fg=DIM, bg=PANEL)

    tab_np  = tk.Label(tab_bar, text="NON-PREEMPTIVE", bg=PANEL, fg=ACCENT_G,
                       font=F_TAB, padx=18, pady=10, cursor="hand2")
    tab_pre = tk.Label(tab_bar, text="PREEMPTIVE",     bg=PANEL, fg=DIM,
                       font=F_TAB, padx=18, pady=10, cursor="hand2")

    tab_np.pack(side="left")
    tk.Frame(tab_bar, bg=BORDER, width=1).pack(side="left", fill="y", pady=6)
    tab_pre.pack(side="left")

    tab_np.bind("<Button-1>",  lambda _: _show(np_panel,  tab_np,  ACCENT_G, tab_pre))
    tab_pre.bind("<Button-1>", lambda _: _show(pre_panel, tab_pre, ACCENT_B, tab_np))

    tab_np.bind("<Enter>",  lambda _: tab_np.configure(fg=ACCENT_G)
                            if tab_np.cget("fg") != str(ACCENT_G) else None)
    tab_pre.bind("<Enter>", lambda _: tab_pre.configure(fg=TEXT)
                            if tab_pre.cget("fg") == str(DIM) else None)
    tab_pre.bind("<Leave>", lambda _: tab_pre.configure(fg=DIM)
                            if tab_pre.cget("fg") == str(TEXT) else None)

    np_panel.place(relx=0, rely=0, relwidth=1, relheight=1)
    _active[0] = np_panel

    return tab_np, tab_pre


def build_section_header(parent, title: str, subtitle: str, accent: str):
    row = tk.Frame(parent, bg=BG, padx=24, pady=14)
    row.pack(fill="x")
    tk.Label(row, text=title,    bg=BG, fg=accent,  font=F_SECTION).pack(side="left")
    tk.Label(row, text=subtitle, bg=BG, fg=SUBTEXT, font=F_DESC).pack(side="right")
    h_rule(parent, BORDER)


def styled_entry(parent, show="", width=28, accent=ACCENT_B):
    e = tk.Entry(parent, show=show, bg=BORDER, fg=TEXT,
                 insertbackground=accent, relief="flat",
                 font=(MONO, 11), width=width,
                 highlightthickness=1,
                 highlightcolor=accent,
                 highlightbackground=PANEL)
    return e


def styled_label(parent, text, size=9, color=None):
    tk.Label(parent, text=text, bg=PANEL,
             fg=color or SUBTEXT,
             font=(MONO, size, "bold")).pack(anchor="w", padx=30, pady=(8, 0))


def setup_treeview_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.Treeview",
                    background=PANEL,
                    foreground=TEXT,
                    fieldbackground=PANEL,
                    bordercolor=BORDER,
                    rowheight=28,
                    font=(MONO, 10))
    style.configure("Dark.Treeview.Heading",
                    background=BORDER,
                    foreground=ACCENT_G,
                    relief="flat",
                    font=(MONO, 9, "bold"))
    style.map("Dark.Treeview",
              background=[("selected", ACCENT_B)],
              foreground=[("selected", BG)])


def build_footer(parent, on_exit):
    h_rule(parent, BORDER)
    foot = tk.Frame(parent, bg=PANEL, padx=20, pady=10)
    foot.pack(fill="x", side="bottom")
    tk.Label(foot, text="●  READY", bg=PANEL, fg=ACCENT_G,
             font=F_FOOTER).pack(side="left")
    exit_btn = tk.Label(foot, text="[ EXIT ]", bg=PANEL, fg=ACCENT_R,
                        font=(MONO, 9, "bold"), padx=8, cursor="hand2")
    exit_btn.pack(side="right")
    exit_btn.bind("<Button-1>", lambda _: on_exit())
    exit_btn.bind("<Enter>",    lambda _: exit_btn.configure(bg=ACCENT_R, fg=BG))
    exit_btn.bind("<Leave>",    lambda _: exit_btn.configure(bg=PANEL,    fg=ACCENT_R))