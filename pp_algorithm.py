# prio_preemptive_gui.py
from theme import *

def priority_preemptive_gui():

    win = AlgoWindow("Priority Scheduling (Preemptive)", ACCENT_B)
    body = win.body

    # ==============================
    # INPUT SECTION
    # ==============================
    section_header(body, "INPUT PROCESS DATA")

    frame_count, entry_count = Widgets.count_bar(body, "Process Count", ACCENT_B)
    frame_count.pack(fill="x", padx=16)

    entries = []

    def build_inputs():
        nonlocal entries

        for w in entries:
            for item in w:
                item.destroy()
        entries.clear()

        try:
            n = int(entry_count.get())
            if n < 1:
                raise ValueError
        except:
            Widgets.error(win, "Invalid process count")
            return

        for i in range(n):

            row1, at = Widgets.labelled_entry(body, f"P{i+1} Arrival Time", ACCENT_B)
            row2, bt = Widgets.labelled_entry(body, f"P{i+1} Burst Time", ACCENT_B)
            row3, pr = Widgets.labelled_entry(body, f"P{i+1} Priority (lower = higher)", ACCENT_B)

            row1.pack(fill="x", padx=16, pady=2)
            row2.pack(fill="x", padx=16, pady=2)
            row3.pack(fill="x", padx=16, pady=2)

            entries.append((at, bt, pr, row1, row2, row3))

    Widgets.button(body, "GENERATE INPUT FIELDS", build_inputs, ACCENT_B).pack(pady=10)

    # ==============================
    # OUTPUT
    # ==============================
    section_header(body, "RESULTS")

    output = Widgets.output_box(body, height=22, accent=ACCENT_B)

    def run():

        try:
            arrival = []
            burst = []
            priority = []

            for at, bt, pr, *_ in entries:
                arrival.append(int(at.get()))
                burst.append(int(bt.get()))
                priority.append(int(pr.get()))

            n = len(arrival)

        except:
            Widgets.error(win, "Invalid input values")
            return

        # ==============================
        # ALGORITHM CORE (GUI VERSION)
        # ==============================
        remaining = burst[:]
        completed = [False] * n

        start = [-1] * n
        finish = [0] * n

        time = 0
        done = 0

        gantt = []       # [label, start, end]
        gantt_time = [0]

        while done < n:

            idx = -1
            best = float("inf")

            for i in range(n):
                if arrival[i] <= time and remaining[i] > 0:
                    if priority[i] < best:
                        best = priority[i]
                        idx = i

            # IDLE
            if idx == -1:
                if gantt and gantt[-1][0] == "ID":
                    gantt[-1][2] += 1
                else:
                    gantt.append(["ID", time, time + 1])

                time += 1
                gantt_time.append(time)
                continue

            label = f"P{idx+1}"

            if start[idx] == -1:
                start[idx] = time

            # Gantt merge
            if gantt and gantt[-1][0] == label:
                gantt[-1][2] += 1
            else:
                gantt.append([label, time, time + 1])

            remaining[idx] -= 1
            time += 1
            gantt_time.append(time)

            if remaining[idx] == 0:
                finish[idx] = time
                completed[idx] = True
                done += 1

        # ==============================
        # COMPUTE METRICS
        # ==============================
        tat = []
        wt = []

        total_tat = 0
        total_wt = 0

        for i in range(n):
            t = finish[i] - arrival[i]
            w = t - burst[i]

            tat.append(t)
            wt.append(w)

            total_tat += t
            total_wt += w

        cpu_busy = sum(burst)
        total_time = gantt_time[-1]

        util = (cpu_busy / total_time) * 100
        throughput = n / total_time

        # ==============================
        # OUTPUT RENDERING
        # ==============================
        out = Output(output)
        out.clear()

        # Gantt
        out.line("GANTT CHART:", "header")
        for g in gantt:
            out.line(f"| {g[0]} ", None, "")
        out.line("|")

        for g in gantt:
            out.line(f"{g[1]:<5}", "dim", "")
        out.line(f"{gantt[-1][2]:<5}")

        out.blank()

        # Table
        out.line("PROCESS TABLE:", "header")

        widths = [12, 10, 10, 10, 12, 10]
        out.table_row("PID", "AT", "BT", "PR", "TAT", "WT", widths=widths, tag="bold")

        for i in range(n):
            out.table_row(
                f"P{i+1}",
                arrival[i],
                burst[i],
                priority[i],
                tat[i],
                wt[i],
                widths=widths
            )

        out.blank()

        # Performance
        out.line("SYSTEM PERFORMANCE", "header")
        out.kv("CPU Busy Time", cpu_busy)
        out.kv("CPU Idle Time", total_time - cpu_busy)
        out.kv("CPU Utilization", f"{util:.2f}%")
        out.kv("Throughput", throughput)
        out.kv("Avg Waiting Time", total_wt / n)
        out.kv("Avg Turnaround Time", total_tat / n)

        win.set_status("Completed", ACCENT_B)

    Widgets.button(body, "RUN PRIORITY SCHEDULING", run, ACCENT_B, width=30).pack(pady=20)

    win.mainloop()