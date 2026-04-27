import tkinter as tk
import random
from theme import (
    AlgoWindow, Widgets, Output, section_header, h_rule,
    ACCENT_B, ACCENT_R, ACCENT_Y, BG, PANEL, CARD, BORDER, TEXT, SUBTEXT, MONO
)


# ─────────────────────────────────────────────
#  PERFORMANCE LABEL HELPER
# ─────────────────────────────────────────────
# Converts raw CPU utilization and throughput numbers into
# human-readable labels (e.g. "Good", "High") and short
# explanations shown in the output section.
def _perf_labels(cpu_util, throughput):
    # CPU utilization thresholds
    if cpu_util < 40:    cpu_label, cpu_meaning = "Poor",  "CPU is mostly idle (underutilized)."
    elif cpu_util < 70:  cpu_label, cpu_meaning = "Fair",  "Moderate CPU usage."
    elif cpu_util <= 90: cpu_label, cpu_meaning = "Good",  "Efficient CPU usage."
    else:                cpu_label, cpu_meaning = "High",  "Very high CPU load."

    # Throughput thresholds (processes completed per unit time)
    if throughput < 0.5: tp_label, tp_meaning = "Low",      "Few processes completed."
    elif throughput <= 1:tp_label, tp_meaning = "Moderate", "Balanced completion rate."
    else:                tp_label, tp_meaning = "High",     "Fast process completion."

    return cpu_label, cpu_meaning, tp_label, tp_meaning


# ─────────────────────────────────────────────
#  CORE ROUND ROBIN SCHEDULING ALGORITHM
# ─────────────────────────────────────────────
# Simulates the Round Robin (RR) CPU scheduling algorithm.
#
# OVERVIEW:
#   - Each process gets a fixed CPU time slice (time quantum).
#   - If unfinished, it is placed back at the end of the queue.
#   - The CPU cycles through processes in FIFO order.
#   - This is a PREEMPTIVE scheduling algorithm.
#
# PARAMETERS:
#   process_count : int   → number of processes
#   arrival_time  : list  → arrival times of processes
#   burst_time    : list  → required CPU time per process
#   time_quantum  : int   → max CPU time per turn
def _run_rr(process_count, arrival_time, burst_time, time_quantum):

    # Copy of burst times to track remaining execution per process
    remaining_burst = burst_time.copy()

    # Stores first execution time (-1 means not yet started)
    start_time  = [-1] * process_count

    # Stores completion time of each process
    finish_time = [0] * process_count

    current_time  = 0        # Simulated clock
    queue         = []       # Ready queue (FIFO)
    completed     = 0        # Count of completed processes
    cpu_idle_time = 0        # Total idle time

    # Tracks whether a process has already entered the queue
    entered = [False] * process_count

    # Gantt chart: (label, start_time, end_time)
    gantt_chart = []

    # ── MAIN SIMULATION LOOP ───────────────────
    while completed < process_count:

        # STEP 1: Add newly arrived processes to queue
        for i in range(process_count):
            if arrival_time[i] <= current_time and not entered[i]:
                queue.append(i)
                entered[i] = True

        # STEP 2: Handle CPU idle state
        if not queue:
            start = current_time
            current_time  += 1
            cpu_idle_time += 1
            end = current_time

            # Merge consecutive idle blocks
            if gantt_chart and gantt_chart[-1][0] == "IDLE" and gantt_chart[-1][2] == start:
                gantt_chart[-1] = ("IDLE", gantt_chart[-1][1], end)
            else:
                gantt_chart.append(("IDLE", start, end))
            continue

        # STEP 3: Select next process (FIFO)
        current = queue.pop(0)

        # Record first CPU access
        if start_time[current] == -1:
            start_time[current] = current_time

        # STEP 4: Execute process (bounded by time quantum)
        execute_time = min(time_quantum, remaining_burst[current])

        start = current_time
        current_time += execute_time
        remaining_burst[current] -= execute_time
        end = current_time

        # Record execution in Gantt chart
        label = f"P{current + 1}"
        if gantt_chart and gantt_chart[-1][0] == label and gantt_chart[-1][2] == start:
            gantt_chart[-1] = (label, gantt_chart[-1][1], end)
        else:
            gantt_chart.append((label, start, end))

        # STEP 5: Add processes that arrived during execution
        for i in range(process_count):
            if arrival_time[i] <= current_time and not entered[i]:
                queue.append(i)
                entered[i] = True

        # STEP 6: Check completion or requeue
        if remaining_burst[current] > 0:
            queue.append(current)  # Not finished → requeue
        else:
            finish_time[current] = current_time
            completed += 1

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

    # ── SYSTEM PERFORMANCE METRICS ────────────
    cpu_busy_time = sum(burst_time)
    total_time    = gantt_chart[-1][2]

    cpu_util   = (cpu_busy_time / total_time) * 100
    throughput = process_count / total_time

    cpu_label, cpu_meaning, tp_label, tp_meaning = _perf_labels(cpu_util, throughput)

    # ── RETURN RESULTS ────────────────────────
    return dict(
        process_count       = process_count,
        arrival_time        = arrival_time,
        burst_time          = burst_time,
        time_quantum        = time_quantum,
        turnaround_time     = turnaround_time,
        waiting_time        = waiting_time,
        total_turnaround    = total_turnaround,
        total_waiting       = total_waiting,
        gantt_chart         = gantt_chart,
        cpu_busy_time       = cpu_busy_time,
        cpu_idle_time       = cpu_idle_time,
        cpu_utilization     = cpu_util,
        throughput          = throughput,
        avg_waiting_time    = total_waiting    / process_count,
        avg_turnaround_time = total_turnaround / process_count,
        cpu_label           = cpu_label,
        cpu_meaning         = cpu_meaning,
        throughput_label    = tp_label,
        throughput_meaning  = tp_meaning,
    )


# ─────────────────────────────────────────────
#  GUI – MAIN WINDOW
# ─────────────────────────────────────────────
# Builds and opens the Round Robin input/output window.
# The GUI is split into three input steps and one output area:
#   Step 1 – Enter the number of processes
#   Step 2 – Enter the time quantum
#   Step 3 – Enter arrival and burst times per process
#   Output – Gantt chart, process table, and performance summary
def round_robin_gui():
    win = AlgoWindow("Round Robin  –  Preemptive", accent=ACCENT_B, width=800, height=700)
    win.state("zoomed")  # Start maximized

    # ── Step 1: Process count input ───────────────────────────────────────
    section_header(win.body, "STEP 1  –  PROCESS COUNT", accent=ACCENT_B)
    count_bar, count_entry = Widgets.count_bar(win.body, "Number of processes")
    count_bar.pack(fill="x", padx=16, pady=(4, 2))
    h_rule(win.body, BORDER)

    # ── Step 2: Time quantum input ────────────────────────────────────────
    section_header(win.body, "STEP 2  –  TIME QUANTUM", accent=ACCENT_B)
    tq_bar = tk.Frame(win.body, bg=PANEL, padx=16, pady=10)
    tq_bar.pack(fill="x")
    tk.Label(tq_bar, text="Time quantum", bg=PANEL, fg=SUBTEXT, font=(MONO, 10)).pack(side="left")
    tq_entry = tk.Entry(
        tq_bar, bg=BORDER, fg=TEXT, insertbackground=ACCENT_B,
        relief="flat", font=(MONO, 10), width=5,
        highlightthickness=1, highlightcolor=ACCENT_B, highlightbackground=BORDER
    )
    tq_entry.pack(side="left", padx=10)
    h_rule(win.body, BORDER)

    # ── Step 3: Arrival & burst time table ───────────────────────────────
    section_header(win.body, "STEP 3  –  ARRIVAL & BURST TIMES", accent=ACCENT_B)
    table_host = tk.Frame(win.body, bg=BG)
    table_host.pack(fill="x", padx=16, pady=(0, 4))

    # Column headers for the process input table
    col_hdr = tk.Frame(table_host, bg=CARD)
    col_hdr.pack(fill="x", pady=(0, 2))
    for txt, w in [("Process", 8), ("Arrival Time", 14), ("Burst Time", 14)]:
        tk.Label(
            col_hdr, text=txt, bg=CARD, fg=SUBTEXT,
            font=(MONO, 8, "bold"), width=w, anchor="w", padx=8, pady=6
        ).pack(side="left")

    entry_rows = []  # Stores (arrival_entry, burst_entry) pairs for each process row

    # ── Inner: Build process input rows ──────────────────────────────────
    # Dynamically creates one input row per process.
    # Called when the user confirms the process count.
    def _build(n):
        # Remove any previously generated rows (keep the header)
        for w in table_host.winfo_children()[1:]:
            w.destroy()
        entry_rows.clear()

        for i in range(n):
            # Alternate row background color for readability
            row = tk.Frame(table_host, bg=PANEL if i % 2 == 0 else CARD)
            row.pack(fill="x", pady=1)

            # Process label (e.g. "P1", "P2", ...)
            tk.Label(
                row, text=f"P{i+1}", bg=row["bg"], fg=ACCENT_B,
                font=(MONO, 10, "bold"), width=8, anchor="w", padx=8
            ).pack(side="left")

            # Two entry fields per row: arrival time and burst time
            es = []
            for _ in range(2):
                e = tk.Entry(
                    row, bg=BORDER, fg=TEXT, insertbackground=ACCENT_B,
                    relief="flat", font=(MONO, 10), width=12,
                    highlightthickness=1, highlightcolor=ACCENT_B, highlightbackground=BORDER
                )
                e.pack(side="left", padx=(0, 8), pady=5)
                es.append(e)
            entry_rows.append(es)

    # ── Inner: Confirm process count ──────────────────────────────────────
    # Validates the count entry and builds the process table rows.
    def _confirm():
        try:
            n = int(count_entry.get())
            if n < 1:
                raise ValueError
        except ValueError:
            Widgets.error(win, "Process count must be a positive integer.")
            return
        _build(n)
        win.set_status(f"{n} processes loaded")

    # ── Inner: Randomize inputs ───────────────────────────────────────────
    # Fills all entry fields with random but valid values for quick testing.
    # Arrival times are sorted so earlier processes arrive first.
    def _randomize():
        try:
            n = int(count_entry.get())
            if n < 1:
                raise ValueError
        except ValueError:
            Widgets.error(win, "Confirm a process count first.")
            return

        if not entry_rows:
            _build(n)

        # Auto-fill time quantum if empty
        if not tq_entry.get():
            tq_entry.insert(0, str(random.randint(1, 5)))

        # Generate sorted random arrival times so processes arrive in order
        pool = sorted(random.randint(0, 10) for _ in range(n))
        for i, (at_e, bt_e) in enumerate(entry_rows):
            at_e.delete(0, "end"); at_e.insert(0, str(pool[i]))
            bt_e.delete(0, "end"); bt_e.insert(0, str(random.randint(1, 10)))

        win.set_status("Random values generated – press RUN to simulate")

    # Attach CONFIRM and RANDOM buttons to the count bar
    Widgets.button(count_bar, "CONFIRM", _confirm, accent=ACCENT_B, width=10).pack(side="left", padx=10)
    Widgets.button(count_bar, "RANDOM",  _randomize, accent=ACCENT_Y, width=10).pack(side="left", padx=(0, 10))
    h_rule(win.body, BORDER)

    btn_row = tk.Frame(win.body, bg=BG, pady=8)
    btn_row.pack(fill="x", padx=16)

    section_header(win.body, "OUTPUT", subtitle="gantt chart · process table · performance", accent=ACCENT_B)
    out = Output(Widgets.output_box(win.body, height=32, accent=ACCENT_B))

    # ── Inner: Run the simulation ─────────────────────────────────────────
    # Reads all inputs, validates them, runs the RR algorithm, and renders results.
    def _run():
        if not entry_rows:
            Widgets.error(win, "Confirm process count first.")
            return

        # Validate time quantum
        try:
            tq = int(tq_entry.get())
            if tq <= 0:
                raise ValueError("Time quantum must be positive.")
        except ValueError as e:
            Widgets.error(win, str(e))
            return

        # Read and validate each process's arrival and burst times
        arrival, burst = [], []
        for i, (at_e, bt_e) in enumerate(entry_rows):
            try:
                at = int(at_e.get())
                bt = int(bt_e.get())
                if at < 0:  raise ValueError("Arrival time cannot be negative.")
                if bt <= 0: raise ValueError("Burst time must be positive.")
                arrival.append(at)
                burst.append(bt)
            except ValueError as e:
                Widgets.error(win, f"P{i+1}: {e}")
                return

        # Run the algorithm and render the results
        _render(out, _run_rr(len(entry_rows), arrival, burst, tq))
        win.set_status("Simulation complete", color=ACCENT_B)

    # ── Inner: Clear all inputs and output ───────────────────────────────
    def _clear():
        out.clear()
        count_entry.delete(0, "end")
        tq_entry.delete(0, "end")
        for w in table_host.winfo_children()[1:]:
            w.destroy()
        entry_rows.clear()
        win.set_status("Cleared")

    # Attach RUN and CLEAR buttons to the button row
    Widgets.button(btn_row, "▶  RUN",    _run,   accent=ACCENT_B, width=14).pack(side="left", padx=(0, 8))
    Widgets.button(btn_row, "✕  CLEAR",  _clear, accent=ACCENT_R, width=12).pack(side="left")
    win.grab_set()


# ─────────────────────────────────────────────
#  OUTPUT RENDERER
# ─────────────────────────────────────────────
# Takes the results dictionary from _run_rr() and writes
# three sections to the output box:
#   1. Gantt Chart   – visual timeline of CPU execution
#   2. Process Table – per-process turnaround and waiting times
#   3. System Performance – CPU utilization, throughput, averages
def _render(out, r):
    out.clear()
    n = r["process_count"]

    # ── Section 1: Gantt Chart ────────────────────────────────────────────
    # Displays a text-based bar showing which process (or IDLE) ran at each time slot.
    # Format:  │ P1   │ P2   │ IDLE  │ P1   │
    #          0      3      6      7      10
    out.line(f"  GANTT CHART   (quantum = {r['time_quantum']})", tag="header")
    out.blank()

    # Build the top bar with process labels
    bar = "  "
    for g in r["gantt_chart"]:
        bar += f"│{g[0]:^6}"
    out.line(bar + "│", tag="accent")

    # Build the timeline row with start times (and final end time at the right)
    tl = "  "
    for g in r["gantt_chart"]:
        tl += f"{g[1]:<7}"
    tl += str(r["gantt_chart"][-1][2])
    out.line(tl, tag="dim")
    out.blank()
    out.divider()

    # ── Section 2: Process Table ──────────────────────────────────────────
    # Shows each process's arrival, burst, turnaround, and waiting times.
    out.line("  PROCESS TABLE", tag="header")
    out.blank()

    W = [6, 14, 12, 14, 14]  # Column widths for alignment
    out.table_row("PID", "Arrival", "Burst", "Turnaround", "Waiting", widths=W, tag="bold")
    out.divider("─", 62, tag="dim")

    for i in range(n):
        out.table_row(
            f"P{i+1}",
            r["arrival_time"][i],
            r["burst_time"][i],
            r["turnaround_time"][i],
            r["waiting_time"][i],
            widths=W,
            tag="accent" if i % 2 == 0 else None  # Alternating row highlight
        )

    out.divider("─", 62, tag="dim")
    # Totals row
    out.table_row("Total", "", "", r["total_turnaround"], r["total_waiting"], widths=W, tag="bold")
    out.blank()
    out.divider()

    # ── Section 3: System Performance ────────────────────────────────────
    # Summary of how well the CPU was utilized and how fast processes completed.
    out.line("  SYSTEM PERFORMANCE", tag="header")
    out.blank()

    out.kv("CPU Busy Time",        r["cpu_busy_time"])
    out.kv("CPU Idle Time",        r["cpu_idle_time"])
    out.kv("CPU Utilization (%)",  f"{r['cpu_utilization']:.2f}  [{r['cpu_label']}]")
    out.line(f"    → {r['cpu_meaning']}", tag="dim")
    out.kv("Throughput",           f"{r['throughput']:.4f}  [{r['throughput_label']}]")
    out.line(f"    → {r['throughput_meaning']}", tag="dim")
    out.kv("Avg Waiting Time",     f"{r['avg_waiting_time']:.2f}")
    out.kv("Avg Turnaround Time",  f"{r['avg_turnaround_time']:.2f}")
    out.blank()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
# Only runs the GUI when this file is executed directly.
# If imported by another module (e.g. main_menu.py), the GUI
# will NOT launch automatically — call round_robin_gui() explicitly.
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()       # Hide the default blank root window
    round_robin_gui()
    root.mainloop()