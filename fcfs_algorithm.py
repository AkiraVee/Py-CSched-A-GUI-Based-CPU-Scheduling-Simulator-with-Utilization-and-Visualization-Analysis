import tkinter as tk
import random
from theme import (
    AlgoWindow, Widgets, Output, section_header, h_rule,
    ACCENT_G, ACCENT_R, ACCENT_Y, BG, PANEL, CARD, BORDER, TEXT, SUBTEXT, MONO
)


# ─────────────────────────────────────────────
# FCFS LOGIC
# Sorts processes by arrival time, then runs
# each one fully before moving to the next.
# If the CPU is free, an IDLE block is added.
# ─────────────────────────────────────────────
def _run_fcfs(process_count, arrival_time, burst_time):

    # Sort processes by who arrives first
    processes = list(range(process_count))
    processes.sort(key=lambda x: arrival_time[x])

    start_time   = [0] * process_count
    finish_time  = [0] * process_count
    current_time = 0
    gantt_chart  = []   # labels shown on the Gantt chart
    gantt_time   = [0]  # time markers below the Gantt chart

    for i in processes:
        # If CPU has nothing to do, insert an IDLE block
        if current_time < arrival_time[i]:
            gantt_chart.append("IDLE")
            current_time = arrival_time[i]

        start_time[i] = current_time
        if gantt_time[-1] != current_time:
            gantt_time.append(current_time)

        # Run the process for its full burst time
        gantt_chart.append(f"P{i+1}")
        current_time  += burst_time[i]
        finish_time[i] = current_time
        gantt_time.append(current_time)

    # Calculate turnaround and waiting time for each process
    turnaround_time  = []
    waiting_time     = []
    total_turnaround = 0
    total_waiting    = 0

    for i in range(process_count):
        tat = finish_time[i] - arrival_time[i]  # how long from arrival to finish
        wt  = tat - burst_time[i]               # time spent waiting (not running)
        turnaround_time.append(tat)
        waiting_time.append(wt)
        total_turnaround += tat
        total_waiting    += wt

    cpu_busy_time   = sum(burst_time)
    total_time      = gantt_time[-1]
    cpu_utilization = (cpu_busy_time / total_time) * 100
    throughput      = process_count / total_time

    # Rate the CPU utilization
    if cpu_utilization < 40:
        cpu_label, cpu_meaning = "Poor",  "CPU is mostly idle (underutilized)."
    elif cpu_utilization < 70:
        cpu_label, cpu_meaning = "Fair",  "Moderate CPU usage."
    elif cpu_utilization <= 90:
        cpu_label, cpu_meaning = "Good",  "Efficient CPU usage."
    else:
        cpu_label, cpu_meaning = "High",  "Very high CPU load."

    # Rate the throughput
    if throughput < 0.5:
        throughput_label, throughput_meaning = "Low",      "Few processes completed."
    elif throughput <= 1:
        throughput_label, throughput_meaning = "Moderate", "Balanced completion rate."
    else:
        throughput_label, throughput_meaning = "High",     "Fast process completion."

    return dict(
        process_count=process_count, arrival_time=arrival_time,
        burst_time=burst_time, turnaround_time=turnaround_time,
        waiting_time=waiting_time, total_turnaround=total_turnaround,
        total_waiting=total_waiting, gantt_chart=gantt_chart,
        gantt_time=gantt_time, cpu_busy_time=cpu_busy_time,
        cpu_idle_time=total_time - cpu_busy_time,
        cpu_utilization=cpu_utilization, throughput=throughput,
        avg_waiting_time=total_waiting    / process_count,
        avg_turnaround_time=total_turnaround / process_count,
        cpu_label=cpu_label, cpu_meaning=cpu_meaning,
        throughput_label=throughput_label, throughput_meaning=throughput_meaning,
    )


# ─────────────────────────────────────────────
# INPUT PANEL
# Builds the step-by-step input form:
#   Step 1 – enter how many processes
#   Step 2 – enter arrival and burst times
# Also includes a RANDOM button to auto-fill.
# ─────────────────────────────────────────────
def _input_panel(win):
    section_header(win.body, "STEP 1  –  PROCESS COUNT", accent=ACCENT_G)

    count_bar, count_entry = Widgets.count_bar(win.body, "Number of processes")
    count_bar.pack(fill="x", padx=16, pady=(4, 2))
    h_rule(win.body, BORDER)

    section_header(win.body, "STEP 2  –  ARRIVAL & BURST TIMES", accent=ACCENT_G)

    # Table container
    table_host = tk.Frame(win.body, bg=BG)
    table_host.pack(fill="x", padx=16, pady=(0, 4))

    # Column headers
    col_hdr = tk.Frame(table_host, bg=CARD)
    col_hdr.pack(fill="x", pady=(0, 2))
    for txt, w in [("Process", 8), ("Arrival Time", 14), ("Burst Time", 14)]:
        tk.Label(col_hdr, text=txt, bg=CARD, fg=SUBTEXT,
                 font=(MONO, 8, "bold"), width=w,
                 anchor="w", padx=8, pady=6).pack(side="left")

    entry_rows = []  # stores (arrival_entry, burst_entry) for each process

    def _build(n):
        # Remove old rows and rebuild for n processes
        for w in table_host.winfo_children()[1:]:
            w.destroy()
        entry_rows.clear()
        for i in range(n):
            # Alternate row background for readability
            row = tk.Frame(table_host, bg=PANEL if i % 2 == 0 else CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"P{i+1}", bg=row["bg"], fg=ACCENT_G,
                     font=(MONO, 10, "bold"), width=8,
                     anchor="w", padx=8).pack(side="left")
            entries = []
            for _ in range(2):  # arrival and burst columns
                e = tk.Entry(row, bg=BORDER, fg=TEXT,
                             insertbackground=ACCENT_G,
                             relief="flat", font=(MONO, 10), width=12,
                             highlightthickness=1,
                             highlightcolor=ACCENT_G,
                             highlightbackground=BORDER)
                e.pack(side="left", padx=(0, 8), pady=5)
                entries.append(e)
            entry_rows.append(entries)

    def _confirm():
        # Validate count and build the table
        try:
            n = int(count_entry.get())
            if n < 1:
                raise ValueError
        except ValueError:
            Widgets.error(win, "Process count must be a positive integer.")
            return
        _build(n)
        win.set_status(f"{n} processes loaded – fill in times and press RUN")

    def _randomize():
        # Fill all fields with random values for quick testing
        try:
            n = int(count_entry.get())
            if n < 1:
                raise ValueError
        except ValueError:
            Widgets.error(win, "Confirm a process count first.")
            return
        if not entry_rows:
            _build(n)
        arrival_pool = sorted(random.randint(0, 10) for _ in range(n))
        for i, (at_e, bt_e) in enumerate(entry_rows):
            at_e.delete(0, "end"); at_e.insert(0, str(arrival_pool[i]))
            bt_e.delete(0, "end"); bt_e.insert(0, str(random.randint(1, 10)))
        win.set_status("Random values generated – press RUN to simulate")

    Widgets.button(count_bar, "CONFIRM", _confirm,   accent=ACCENT_G, width=10).pack(side="left", padx=10)
    Widgets.button(count_bar, "RANDOM",  _randomize, accent=ACCENT_Y, width=10).pack(side="left", padx=(0, 10))

    return entry_rows, table_host, count_entry


# ─────────────────────────────────────────────
# GUI ENTRY POINT
# Opens the FCFS window, wires up RUN/CLEAR,
# and displays results in the output box.
# ─────────────────────────────────────────────
def fcfs_gui():
    win = AlgoWindow("FCFS  –  First Come First Serve", accent=ACCENT_G, width=800, height=660)
    win.state("zoomed")

    entry_rows, table_host, count_entry = _input_panel(win)

    h_rule(win.body, BORDER)

    # RUN and CLEAR buttons
    btn_row = tk.Frame(win.body, bg=BG, pady=8)
    btn_row.pack(fill="x", padx=16)

    section_header(win.body, "OUTPUT",
                   subtitle="gantt chart · process table · performance",
                   accent=ACCENT_G)

    out = Output(Widgets.output_box(win.body, height=32, accent=ACCENT_G))

    def _run():
        # Read and validate all inputs, then run the algorithm
        if not entry_rows:
            Widgets.error(win, "Confirm process count first.")
            return
        arrival, burst = [], []
        for i, (at_e, bt_e) in enumerate(entry_rows):
            try:
                at = int(at_e.get()); bt = int(bt_e.get())
                if at < 0:  raise ValueError("Arrival time cannot be negative.")
                if bt <= 0: raise ValueError("Burst time must be positive.")
                arrival.append(at); burst.append(bt)
            except ValueError as e:
                Widgets.error(win, f"P{i+1}: {e}"); return
        _render(out, _run_fcfs(len(entry_rows), arrival, burst))
        win.set_status("Simulation complete", color=ACCENT_G)

    def _clear():
        # Reset everything back to blank
        out.clear()
        count_entry.delete(0, "end")
        for w in table_host.winfo_children()[1:]:
            w.destroy()
        entry_rows.clear()
        win.set_status("Cleared – enter a new process count")

    Widgets.button(btn_row, "▶  RUN",   _run,   accent=ACCENT_G, width=14).pack(side="left", padx=(0, 8))
    Widgets.button(btn_row, "✕  CLEAR", _clear, accent=ACCENT_R, width=12).pack(side="left")
    win.grab_set()


# ─────────────────────────────────────────────
# OUTPUT RENDERER
# Writes the Gantt chart, process table, and
# system performance into the output text box.
# ─────────────────────────────────────────────
def _render(out, r):
    out.clear()
    n = r["process_count"]

    # Gantt chart – visual bar showing execution order
    out.line("  GANTT CHART", tag="header")
    out.blank()
    bar = "  "
    for p in r["gantt_chart"]:
        bar += f"│{p:^6}"
    out.line(bar + "│", tag="accent")
    tl = "  "
    for t in r["gantt_time"]:
        tl += f"{t:<7}"
    out.line(tl, tag="dim")
    out.blank()
    out.divider()

    # Process table – per-process timing breakdown
    out.line("  PROCESS TABLE", tag="header")
    out.blank()
    W = [6, 14, 12, 14, 14]
    out.table_row("PID", "Arrival", "Burst", "Turnaround", "Waiting", widths=W, tag="bold")
    out.divider("─", 62, tag="dim")
    for i in range(n):
        out.table_row(f"P{i+1}", r["arrival_time"][i], r["burst_time"][i],
                      r["turnaround_time"][i], r["waiting_time"][i],
                      widths=W, tag="accent" if i % 2 == 0 else None)
    out.divider("─", 62, tag="dim")
    out.table_row("Total", "", "", r["total_turnaround"], r["total_waiting"], widths=W, tag="bold")
    out.blank()
    out.divider()

    # System performance – overall efficiency metrics
    out.line("  SYSTEM PERFORMANCE", tag="header")
    out.blank()
    out.kv("CPU Busy Time",       r["cpu_busy_time"])
    out.kv("CPU Idle Time",       r["cpu_idle_time"])
    out.kv("CPU Utilization (%)", f"{r['cpu_utilization']:.2f}  [{r['cpu_label']}]")
    out.line(f"    → {r['cpu_meaning']}", tag="dim")
    out.kv("Throughput",          f"{r['throughput']:.4f}  [{r['throughput_label']}]")
    out.line(f"    → {r['throughput_meaning']}", tag="dim")
    out.kv("Avg Waiting Time",    f"{r['avg_waiting_time']:.2f}")
    out.kv("Avg Turnaround Time", f"{r['avg_turnaround_time']:.2f}")
    out.blank()