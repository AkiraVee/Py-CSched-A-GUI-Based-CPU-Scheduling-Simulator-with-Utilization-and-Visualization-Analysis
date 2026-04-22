from theme import *

def fcfs_gui():
    win = AlgoWindow("FCFS - First Come First Serve", ACCENT_G)
    body = win.body

    out = Widgets.output_box(body, height=20, accent=ACCENT_G)
    output = Output(out)

    def run():
        try:
            n = int(entry_count.get())
            at = [int(a.get()) for a in at_entries]
            bt = [int(b.get()) for b in bt_entries]
        except:
            Widgets.error(win, "Invalid input")
            return

        # ===== ORIGINAL LOGIC (UNCHANGED) =====
        processes = list(range(n))
        processes.sort(key=lambda x: at[x])

        start = [0]*n
        finish = [0]*n
        gantt = []
        gantt_time = [0]
        time = 0

        for i in processes:
            if time < at[i]:
                gantt.append("ID")
                time = at[i]

            start[i] = time
            gantt.append(f"P{i+1}")
            time += bt[i]
            finish[i] = time
            gantt_time.append(time)

        tat = [finish[i]-at[i] for i in range(n)]
        wt = [tat[i]-bt[i] for i in range(n)]

        # ===== OUTPUT =====
        output.clear()
        output.line("GANTT CHART:", "header")
        output.line("| " + " | ".join(gantt) + " |")
        output.line(" ".join(map(str, gantt_time)))

        output.blank()
        output.line("PROCESS TABLE:", "header")

        for i in range(n):
            output.line(f"P{i+1}  AT:{at[i]} BT:{bt[i]} TAT:{tat[i]} WT:{wt[i]}")

    # ===== INPUT UI =====
    section_header(body, "INPUT SECTION", accent=ACCENT_G)

    bar, entry_count = Widgets.count_bar(body)
    bar.pack(fill="x", padx=16)

    at_entries, bt_entries = [], []

    def build_inputs():
        for w in input_frame.winfo_children():
            w.destroy()

        n = int(entry_count.get())

        for i in range(n):
            r, e = Widgets.labelled_entry(input_frame, f"P{i+1} Arrival", ACCENT_G)
            r.pack(fill="x")
            at_entries.append(e)

        for i in range(n):
            r, e = Widgets.labelled_entry(input_frame, f"P{i+1} Burst", ACCENT_G)
            r.pack(fill="x")
            bt_entries.append(e)

    Widgets.button(body, "Generate Inputs", build_inputs, ACCENT_G).pack(pady=10)
    Widgets.button(body, "RUN FCFS", run, ACCENT_G).pack(pady=10)

    input_frame = tk.Frame(body, bg=BG)
    input_frame.pack(fill="x", padx=16)