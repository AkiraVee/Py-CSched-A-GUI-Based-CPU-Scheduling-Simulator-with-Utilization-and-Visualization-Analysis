import tkinter as tk
import random
from theme import (
    AlgoWindow, Widgets, Output, section_header, h_rule,
    ACCENT_B, ACCENT_R, ACCENT_Y, BG, PANEL, CARD, BORDER, TEXT, SUBTEXT, MONO
)


def _perf_labels(cpu_util, throughput):
    if cpu_util < 40:    cpu_label, cpu_meaning = "Poor",  "CPU is mostly idle (underutilized)."
    elif cpu_util < 70:  cpu_label, cpu_meaning = "Fair",  "Moderate CPU usage."
    elif cpu_util <= 90: cpu_label, cpu_meaning = "Good",  "Efficient CPU usage."
    else:                cpu_label, cpu_meaning = "High",  "Very high CPU load."
    if throughput < 0.5: tp_label,  tp_meaning  = "Low",      "Few processes completed."
    elif throughput <= 1:tp_label,  tp_meaning  = "Moderate", "Balanced completion rate."
    else:                tp_label,  tp_meaning  = "High",     "Fast process completion."
    return cpu_label, cpu_meaning, tp_label, tp_meaning


# ─────────────────────────────────────────────
#  SRTF (SHORTEST REMAINING TIME FIRST)
# ─────────────────────────────────────────────
# Simulates the SRTF CPU scheduling algorithm.
#
# OVERVIEW:
#   - At every time unit, the process with the
#     SHORTEST remaining burst time is selected.
#   - If a new process arrives with a shorter
#     remaining time, it immediately preempts.
#   - This is a PREEMPTIVE version of SJF.
#
# PARAMETERS:
#   process_count : int   → number of processes
#   arrival_time  : list  → arrival times
#   burst_time    : list  → CPU burst times
def _run_srtf(process_count, arrival_time, burst_time):

    # Remaining execution time per process
    remaining = burst_time.copy()

    # Completion time for each process
    finish_time = [0] * process_count

    current_time  = 0     # Simulation clock
    done          = 0     # Number of completed processes
    cpu_idle_time = 0     # Total idle time

    # Gantt tracking
    gantt = []
    last_label = None
    segment_start = 0

    # ── MAIN SIMULATION LOOP ───────────────────
    while done < process_count:

        # STEP 1: Find process with shortest remaining time
        idx = -1
        min_remaining = float('inf')

        for i in range(process_count):
            if arrival_time[i] <= current_time and remaining[i] > 0:
                if remaining[i] < min_remaining:
                    min_remaining = remaining[i]
                    idx = i

        # STEP 2: If no process is ready → CPU idle
        if idx == -1:
            label = "ID"

            # Start or extend idle segment
            if last_label != label:
                if last_label is not None:
                    gantt.append((last_label, segment_start, current_time))
                segment_start = current_time
                last_label = label

            current_time += 1
            cpu_idle_time += 1
            continue

        label = f"P{idx+1}"

        # STEP 3: Handle context switch (new process takes CPU)
        if last_label != label:
            if last_label is not None:
                gantt.append((last_label, segment_start, current_time))
            segment_start = current_time
            last_label = label

        # STEP 4: Execute process for 1 time unit
        remaining[idx] -= 1
        current_time += 1

        # STEP 5: If process finishes
        if remaining[idx] == 0:
            finish_time[idx] = current_time
            done += 1

    # Finalize last Gantt segment
    if last_label is not None:
        gantt.append((last_label, segment_start, current_time))

    # ── PER-PROCESS METRICS ───────────────────
    turnaround_time = []
    waiting_time    = []
    total_turnaround = 0
    total_waiting    = 0

    for i in range(process_count):
        # Turnaround = Finish − Arrival
        tat = finish_time[i] - arrival_time[i]

        # Waiting = Turnaround − Burst
        wt = tat - burst_time[i]

        turnaround_time.append(tat)
        waiting_time.append(wt)

        total_turnaround += tat
        total_waiting    += wt

    # ── SYSTEM PERFORMANCE ───────────────────
    cpu_busy_time = sum(burst_time)
    total_time    = current_time

    cpu_util   = (cpu_busy_time / total_time) * 100
    throughput = process_count / total_time

    cpu_label, cpu_meaning, tp_label, tp_meaning = _perf_labels(cpu_util, throughput)

    # ── RETURN RESULTS ───────────────────────
    return dict(
        process_count=process_count,
        arrival_time=arrival_time,
        burst_time=burst_time,
        turnaround_time=turnaround_time,
        waiting_time=waiting_time,
        total_turnaround=total_turnaround,
        total_waiting=total_waiting,
        gantt=gantt,
        cpu_busy_time=cpu_busy_time,
        cpu_idle_time=cpu_idle_time,
        cpu_util=cpu_util,
        throughput=throughput,
        avg_waiting_time=total_waiting / process_count,
        avg_turnaround_time=total_turnaround / process_count,
        cpu_label=cpu_label,
        cpu_meaning=cpu_meaning,
        throughput_label=tp_label,
        throughput_meaning=tp_meaning,
    )


# ─────────────────────────────────────────────
# GUI ENTRY POINT
# ─────────────────────────────────────────────
def srtf_gui():
    win = AlgoWindow("SRTF  –  Shortest Remaining Time First", accent=ACCENT_B, width=800, height=660)
    win.state("zoomed")

    section_header(win.body, "STEP 1  –  PROCESS COUNT", accent=ACCENT_B)
    count_bar, count_entry = Widgets.count_bar(win.body, "Number of processes")
    count_bar.pack(fill="x", padx=16, pady=(4, 2))
    h_rule(win.body, BORDER)

    section_header(win.body, "STEP 2  –  ARRIVAL & BURST TIMES", accent=ACCENT_B)
    table_host = tk.Frame(win.body, bg=BG); table_host.pack(fill="x", padx=16, pady=(0, 4))
    col_hdr = tk.Frame(table_host, bg=CARD); col_hdr.pack(fill="x", pady=(0, 2))
    for txt, w in [("Process", 8), ("Arrival Time", 14), ("Burst Time", 14)]:
        tk.Label(col_hdr, text=txt, bg=CARD, fg=SUBTEXT, font=(MONO, 8, "bold"),
                 width=w, anchor="w", padx=8, pady=6).pack(side="left")
    entry_rows = []

    def _build(n):
        for w in table_host.winfo_children()[1:]: w.destroy()
        entry_rows.clear()
        for i in range(n):
            row = tk.Frame(table_host, bg=PANEL if i % 2 == 0 else CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"P{i+1}", bg=row["bg"], fg=ACCENT_B,
                     font=(MONO, 10, "bold"), width=8, anchor="w", padx=8).pack(side="left")
            es = []
            for _ in range(2):
                e = tk.Entry(row, bg=BORDER, fg=TEXT, insertbackground=ACCENT_B,
                             relief="flat", font=(MONO, 10), width=12,
                             highlightthickness=1, highlightcolor=ACCENT_B, highlightbackground=BORDER)
                e.pack(side="left", padx=(0, 8), pady=5); es.append(e)
            entry_rows.append(es)

    def _confirm():
        try:
            n = int(count_entry.get())
            if n < 1: raise ValueError
        except ValueError:
            Widgets.error(win, "Process count must be a positive integer."); return
        _build(n); win.set_status(f"{n} processes loaded")

    def _randomize():
        try:
            n = int(count_entry.get())
            if n < 1: raise ValueError
        except ValueError:
            Widgets.error(win, "Confirm a process count first."); return
        if not entry_rows: _build(n)
        pool = sorted(random.randint(0, 10) for _ in range(n))
        for i, (at_e, bt_e) in enumerate(entry_rows):
            at_e.delete(0, "end"); at_e.insert(0, str(pool[i]))
            bt_e.delete(0, "end"); bt_e.insert(0, str(random.randint(1, 10)))
        win.set_status("Random values generated – press RUN to simulate")

    Widgets.button(count_bar, "CONFIRM", _confirm,   accent=ACCENT_B, width=10).pack(side="left", padx=10)
    Widgets.button(count_bar, "RANDOM",  _randomize, accent=ACCENT_Y, width=10).pack(side="left", padx=(0, 10))
    h_rule(win.body, BORDER)
    btn_row = tk.Frame(win.body, bg=BG, pady=8); btn_row.pack(fill="x", padx=16)
    section_header(win.body, "OUTPUT", subtitle="gantt chart · process table · performance", accent=ACCENT_B)
    out = Output(Widgets.output_box(win.body, height=32, accent=ACCENT_B))

    def _run():
        if not entry_rows: Widgets.error(win, "Confirm process count first."); return
        arrival, burst = [], []
        for i, (at_e, bt_e) in enumerate(entry_rows):
            try:
                at = int(at_e.get()); bt = int(bt_e.get())
                if at < 0:  raise ValueError("Arrival time cannot be negative.")
                if bt <= 0: raise ValueError("Burst time must be positive.")
                arrival.append(at); burst.append(bt)
            except ValueError as e: Widgets.error(win, f"P{i+1}: {e}"); return
        _render(out, _run_srtf(len(entry_rows), arrival, burst))
        win.set_status("Simulation complete", color=ACCENT_B)

    def _clear():
        out.clear(); count_entry.delete(0, "end")
        for w in table_host.winfo_children()[1:]: w.destroy()
        entry_rows.clear(); win.set_status("Cleared")

    Widgets.button(btn_row, "▶  RUN",   _run,   accent=ACCENT_B, width=14).pack(side="left", padx=(0, 8))
    Widgets.button(btn_row, "✕  CLEAR", _clear, accent=ACCENT_R, width=12).pack(side="left")
    win.grab_set()


def _render(out, r):
    out.clear(); n = r["process_count"]
    out.line("  GANTT CHART", tag="header"); out.blank()
    bar = "  "
    for g in r["gantt"]: bar += f"│{g[0]:^6}"
    out.line(bar + "│", tag="accent")
    tl = "  "
    for g in r["gantt"]: tl += f"{g[1]:<7}"
    tl += str(r["gantt"][-1][2])
    out.line(tl, tag="dim"); out.blank(); out.divider()
    out.line("  PROCESS TABLE", tag="header"); out.blank()
    W = [6, 14, 12, 14, 14]
    out.table_row("PID", "Arrival", "Burst", "Turnaround", "Waiting", widths=W, tag="bold")
    out.divider("─", 62, tag="dim")
    for i in range(n):
        out.table_row(f"P{i+1}", r["arrival_time"][i], r["burst_time"][i],
                      r["turnaround_time"][i], r["waiting_time"][i],
                      widths=W, tag="accent" if i % 2 == 0 else None)
    out.divider("─", 62, tag="dim")
    out.table_row("Total", "", "", r["total_turnaround"], r["total_waiting"], widths=W, tag="bold")
    out.blank(); out.divider()
    out.line("  SYSTEM PERFORMANCE", tag="header"); out.blank()
    out.kv("CPU Busy Time",       r["cpu_busy_time"])
    out.kv("CPU Idle Time",       r["cpu_idle_time"])
    out.kv("CPU Utilization (%)", f"{r['cpu_util']:.2f}  [{r['cpu_label']}]")
    out.line(f"    → {r['cpu_meaning']}", tag="dim")
    out.kv("Throughput",          f"{r['throughput']:.4f}  [{r['throughput_label']}]")
    out.line(f"    → {r['throughput_meaning']}", tag="dim")
    out.kv("Avg Waiting Time",    f"{r['avg_waiting_time']:.2f}")
    out.kv("Avg Turnaround Time", f"{r['avg_turnaround_time']:.2f}")
    out.blank()