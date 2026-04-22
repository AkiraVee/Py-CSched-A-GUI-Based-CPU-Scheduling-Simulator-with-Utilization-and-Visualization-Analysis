from theme import *

def srtf_gui():
    win = AlgoWindow("SRTF - Shortest Remaining Time First", ACCENT_B)
    body = win.body

    out = Widgets.output_box(body, accent=ACCENT_B)
    output = Output(out)

    # ==============================
    # RUN LOGIC (UNCHANGED)
    # ==============================
    def run():

        try:
            n = int(entry_count.get())
            at = [int(x.get()) for x in at_entries]
            bt = [int(x.get()) for x in bt_entries]
        except:
            Widgets.error(win, "Invalid input")
            return

        remaining = bt.copy()
        finish = [0] * n

        time = 0
        done = 0
        idle = 0

        gantt = []
        last = None
        start_seg = 0

        while done < n:

            idx = -1
            min_rem = float("inf")

            for i in range(n):
                if at[i] <= time and remaining[i] > 0:
                    if remaining[i] < min_rem:
                        min_rem = remaining[i]
                        idx = i

            # ==============================
            # IDLE CASE
            # ==============================
            if idx == -1:
                label = "ID"

                if last != label:
                    if last is not None:
                        gantt.append((last, start_seg, time))
                    start_seg = time
                    last = label

                time += 1
                idle += 1
                continue

            label = f"P{idx+1}"

            # ==============================
            # CONTEXT SWITCH
            # ==============================
            if last != label:
                if last is not None:
                    gantt.append((last, start_seg, time))
                start_seg = time
                last = label

            remaining[idx] -= 1
            time += 1

            if remaining[idx] == 0:
                finish[idx] = time
                done += 1

        if last is not None:
            gantt.append((last, start_seg, time))

        # ==============================
        # COMPUTE
        # ==============================
        tat = [finish[i] - at[i] for i in range(n)]
        wt = [tat[i] - bt[i] for i in range(n)]

        total_tat = sum(tat)
        total_wt = sum(wt)

        cpu_busy = sum(bt)
        total_time = time

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
            output.line(f"P{i+1} AT:{at[i]} BT:{bt[i]} TAT:{tat[i]} WT:{wt[i]}")

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
    section_header(body, "SRTF INPUT", ACCENT_B)

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

    Widgets.button(body, "Generate Inputs", build_inputs, ACCENT_B).pack(pady=5)
    Widgets.button(body, "RUN SRTF", run, ACCENT_B).pack(pady=10)

    input_frame = tk.Frame(body, bg=BG)
    input_frame.pack(fill="x", padx=16)