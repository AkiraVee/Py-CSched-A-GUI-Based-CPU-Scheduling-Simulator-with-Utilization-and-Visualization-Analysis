from theme import *

def round_robin_gui():
    win = AlgoWindow("Round Robin Scheduling", ACCENT_B)
    body = win.body

    out = Widgets.output_box(body, accent=ACCENT_B)
    output = Output(out)

    # ==============================
    # RUN BUTTON LOGIC (UNCHANGED)
    # ==============================
    def run():

        try:
            n = int(entry_count.get())
            at = [int(x.get()) for x in at_entries]
            bt = [int(x.get()) for x in bt_entries]
            tq = int(time_quantum.get())
        except:
            Widgets.error(win, "Invalid input values")
            return

        # ==============================
        # ORIGINAL LOGIC (UNCHANGED)
        # ==============================
        remaining = bt.copy()
        start_time = [-1] * n
        finish_time = [0] * n

        time = 0
        queue = []
        completed = 0
        idle = 0
        entered = [False] * n

        gantt = []

        while completed < n:

            for i in range(n):
                if at[i] <= time and not entered[i]:
                    queue.append(i)
                    entered[i] = True

            if not queue:
                start = time
                time += 1
                idle += 1
                end = time

                if gantt and gantt[-1][0] == "ID" and gantt[-1][2] == start:
                    gantt[-1] = ("ID", gantt[-1][1], end)
                else:
                    gantt.append(("ID", start, end))
                continue

            current = queue.pop(0)

            if start_time[current] == -1:
                start_time[current] = time

            exec_time = min(tq, remaining[current])

            start = time
            time += exec_time
            remaining[current] -= exec_time
            end = time

            label = f"P{current+1}"

            if gantt and gantt[-1][0] == label and gantt[-1][2] == start:
                gantt[-1] = (label, gantt[-1][1], end)
            else:
                gantt.append((label, start, end))

            for i in range(n):
                if at[i] <= time and not entered[i]:
                    queue.append(i)
                    entered[i] = True

            if remaining[current] > 0:
                queue.append(current)
            else:
                finish_time[current] = time
                completed += 1

        # ==============================
        # METRICS (UNCHANGED)
        # ==============================
        tat = [finish_time[i] - at[i] for i in range(n)]
        wt = [tat[i] - bt[i] for i in range(n)]

        total_tat = sum(tat)
        total_wt = sum(wt)

        cpu_busy = sum(bt)
        total_time = gantt[-1][2]

        # ==============================
        # OUTPUT
        # ==============================
        output.clear()
        output.line("GANTT CHART:", "header")

        output.line("| " + " | ".join([g[0] for g in gantt]) + " |")
        output.line(" ".join(str(g[1]) for g in gantt) + f" {gantt[-1][2]}")

        output.blank()
        output.line("PROCESS TABLE:", "header")

        for i in range(n):
            output.line(
                f"P{i+1} AT:{at[i]} BT:{bt[i]} TAT:{tat[i]} WT:{wt[i]}"
            )

        output.blank()
        output.line("SYSTEM PERFORMANCE:", "header")
        output.line(f"CPU Busy: {cpu_busy}")
        output.line(f"CPU Idle: {idle}")
        output.line(f"Utilization: {(cpu_busy/total_time)*100:.2f}%")
        output.line(f"Throughput: {n/total_time:.2f}")
        output.line(f"Avg WT: {total_wt/n:.2f}")
        output.line(f"Avg TAT: {total_tat/n:.2f}")

    # ==============================
    # UI SECTION
    # ==============================
    section_header(body, "ROUND ROBIN INPUT", ACCENT_B)

    bar, entry_count = Widgets.count_bar(body)
    bar.pack(fill="x")

    at_entries, bt_entries = [], []

    def build_inputs():

        for w in input_frame.winfo_children():
            w.destroy()

        n = int(entry_count.get())

        for i in range(n):
            r, e = Widgets.labelled_entry(input_frame, f"P{i+1} Arrival", ACCENT_B)
            r.pack(fill="x", pady=2)
            at_entries.append(e)

        for i in range(n):
            r, e = Widgets.labelled_entry(input_frame, f"P{i+1} Burst", ACCENT_B)
            r.pack(fill="x", pady=2)
            bt_entries.append(e)

    tq_frame = tk.Frame(body, bg=BG)
    tq_frame.pack(fill="x", padx=16, pady=10)

    tk.Label(tq_frame, text="Time Quantum", bg=BG, fg=SUBTEXT,
             font=F_LABEL).pack(side="left")

    time_quantum = tk.Entry(tq_frame, bg=BORDER, fg=TEXT,
                            insertbackground=ACCENT_B,
                            relief="flat", font=F_INPUT, width=6)
    time_quantum.pack(side="left", padx=10)

    Widgets.button(body, "Generate Inputs", build_inputs, ACCENT_B).pack(pady=5)
    Widgets.button(body, "RUN ROUND ROBIN", run, ACCENT_B).pack(pady=10)

    input_frame = tk.Frame(body, bg=BG)
    input_frame.pack(fill="x", padx=16)