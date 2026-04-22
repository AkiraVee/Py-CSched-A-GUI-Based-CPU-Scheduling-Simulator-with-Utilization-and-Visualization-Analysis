from theme import *

def sjf_gui():
    win = AlgoWindow("SJF - Non Preemptive", ACCENT_G)
    body = win.body

    out = Widgets.output_box(body, accent=ACCENT_G)
    output = Output(out)

    def run():
        try:
            n = int(entry_count.get())
            at = [int(a.get()) for a in at_entries]
            bt = [int(b.get()) for b in bt_entries]
        except:
            Widgets.error(win, "Invalid input")
            return

        completed = [False]*n
        time = 0
        done = 0
        gantt = []
        gantt_time = [0]

        start = [0]*n
        finish = [0]*n

        while done < n:
            idx = -1
            min_bt = 10**9

            for i in range(n):
                if at[i] <= time and not completed[i]:
                    if bt[i] < min_bt:
                        min_bt = bt[i]
                        idx = i

            if idx == -1:
                gantt.append("ID")
                time += 1
                gantt_time.append(time)
                continue

            start[idx] = time
            gantt.append(f"P{idx+1}")
            time += bt[idx]
            finish[idx] = time
            gantt_time.append(time)

            completed[idx] = True
            done += 1

        tat = [finish[i]-at[i] for i in range(n)]
        wt = [tat[i]-bt[i] for i in range(n)]

        output.clear()
        output.line("GANTT CHART:", "header")
        output.line("| " + " | ".join(gantt) + " |")
        output.line(" ".join(map(str, gantt_time)))

        output.blank()
        for i in range(n):
            output.line(f"P{i+1} TAT:{tat[i]} WT:{wt[i]}")

    section_header(body, "SJF INPUT", accent=ACCENT_G)

    bar, entry_count = Widgets.count_bar(body)
    bar.pack(fill="x")

    at_entries, bt_entries = [], []

    def build():
        for w in input_frame.winfo_children():
            w.destroy()

        n = int(entry_count.get())

        for i in range(n):
            r, e = Widgets.labelled_entry(input_frame, f"P{i+1} AT", ACCENT_G)
            r.pack(fill="x")
            at_entries.append(e)

        for i in range(n):
            r, e = Widgets.labelled_entry(input_frame, f"P{i+1} BT", ACCENT_G)
            r.pack(fill="x")
            bt_entries.append(e)

    Widgets.button(body, "Generate", build, ACCENT_G).pack(pady=10)
    Widgets.button(body, "Run SJF", run, ACCENT_G).pack()

    input_frame = tk.Frame(body, bg=BG)
    input_frame.pack(fill="x", padx=16)