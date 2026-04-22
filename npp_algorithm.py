from theme import *

def priority_np_gui():
    win = AlgoWindow("Priority Scheduling (NP)", ACCENT_G)
    body = win.body

    out = Widgets.output_box(body, accent=ACCENT_G)
    output = Output(out)

    def run():
        n = int(entry_count.get())
        at = [int(a.get()) for a in at_entries]
        bt = [int(b.get()) for b in bt_entries]
        pr = [int(p.get()) for p in pr_entries]

        time = 0
        done = 0
        completed = [False]*n

        gantt = []
        gantt_time = [0]

        start = [0]*n
        finish = [0]*n

        while done < n:
            idx = -1
            best = 10**9

            for i in range(n):
                if at[i] <= time and not completed[i]:
                    if pr[i] < best:
                        best = pr[i]
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

        output.clear()
        output.line("GANTT:", "header")
        output.line("| " + " | ".join(gantt))

    # inputs
    section_header(body, "PRIORITY INPUT", ACCENT_G)

    bar, entry_count = Widgets.count_bar(body)
    bar.pack(fill="x")

    at_entries, bt_entries, pr_entries = [], [], []

    def build():
        n = int(entry_count.get())
        for i in range(n):
            r,e = Widgets.labelled_entry(body, f"P{i+1} AT", ACCENT_G)
            r.pack(fill="x"); at_entries.append(e)

            r,e = Widgets.labelled_entry(body, f"P{i+1} BT", ACCENT_G)
            r.pack(fill="x"); bt_entries.append(e)

            r,e = Widgets.labelled_entry(body, f"P{i+1} PR", ACCENT_G)
            r.pack(fill="x"); pr_entries.append(e)

    Widgets.button(body, "Generate", build, ACCENT_G).pack()
    Widgets.button(body, "Run", run, ACCENT_G).pack()