import tkinter as tk
import random
from theme import (
    AlgoWindow, Widgets, Output, section_header, h_rule,
    ACCENT_G, ACCENT_R, ACCENT_Y, BG, PANEL, CARD, BORDER, TEXT, SUBTEXT, MONO
)


def _perf_labels(cpu_utilization, throughput):
    if cpu_utilization < 40:   cpu_label, cpu_meaning = "Poor",     "CPU is mostly idle (underutilized)."
    elif cpu_utilization < 70: cpu_label, cpu_meaning = "Fair",     "Moderate CPU usage."
    elif cpu_utilization <= 90:cpu_label, cpu_meaning = "Good",     "Efficient CPU usage."
    else:                      cpu_label, cpu_meaning = "High",     "Very high CPU load."
    if throughput < 0.5:       tp_label,  tp_meaning  = "Low",      "Few processes completed."
    elif throughput <= 1:      tp_label,  tp_meaning  = "Moderate", "Balanced completion rate."
    else:                      tp_label,  tp_meaning  = "High",     "Fast process completion."
    return cpu_label, cpu_meaning, tp_label, tp_meaning


def _run_sjf(process_count, arrival_time, burst_time):
    completed = [False]*process_count; start_time=[0]*process_count; finish_time=[0]*process_count
    current_time=0; done=0; cpu_idle_time=0; gantt_chart=[]; gantt_time=[0]
    while done < process_count:
        idx=-1; min_burst=float('inf')
        for i in range(process_count):
            if arrival_time[i]<=current_time and not completed[i]:
                if burst_time[i]<min_burst: min_burst=burst_time[i]; idx=i
        if idx==-1:
            next_arrival=min(arrival_time[i] for i in range(process_count) if not completed[i])
            if current_time<next_arrival:
                gantt_chart.append("IDLE"); cpu_idle_time+=next_arrival-current_time
                current_time=next_arrival; gantt_time.append(current_time)
            continue
        start_time[idx]=current_time; gantt_chart.append(f"P{idx+1}")
        current_time+=burst_time[idx]; finish_time[idx]=current_time
        gantt_time.append(current_time); completed[idx]=True; done+=1
    turnaround_time=[]; waiting_time=[]; total_turnaround=0; total_waiting=0
    for i in range(process_count):
        tat=finish_time[i]-arrival_time[i]; wt=tat-burst_time[i]
        turnaround_time.append(tat); waiting_time.append(wt)
        total_turnaround+=tat; total_waiting+=wt
    cpu_busy_time=sum(burst_time); total_time=gantt_time[-1]
    cpu_util=(cpu_busy_time/total_time)*100; throughput=process_count/total_time
    cpu_label,cpu_meaning,tp_label,tp_meaning = _perf_labels(cpu_util, throughput)
    return dict(
        process_count=process_count, arrival_time=arrival_time, burst_time=burst_time,
        turnaround_time=turnaround_time, waiting_time=waiting_time,
        total_turnaround=total_turnaround, total_waiting=total_waiting,
        gantt_chart=gantt_chart, gantt_time=gantt_time,
        cpu_busy_time=cpu_busy_time, cpu_idle_time=cpu_idle_time,
        cpu_util=cpu_util, throughput=throughput,
        avg_waiting_time=total_waiting/process_count,
        avg_turnaround_time=total_turnaround/process_count,
        cpu_label=cpu_label, cpu_meaning=cpu_meaning,
        throughput_label=tp_label, throughput_meaning=tp_meaning,
    )


def sjf_gui():
    win = AlgoWindow("SJF  –  Shortest Job First", accent=ACCENT_G, width=800, height=660)
    win.state("zoomed")

    section_header(win.body, "STEP 1  –  PROCESS COUNT", accent=ACCENT_G)
    count_bar, count_entry = Widgets.count_bar(win.body, "Number of processes")
    count_bar.pack(fill="x", padx=16, pady=(4,2))
    h_rule(win.body, BORDER)

    section_header(win.body, "STEP 2  –  ARRIVAL & BURST TIMES", accent=ACCENT_G)
    table_host = tk.Frame(win.body, bg=BG); table_host.pack(fill="x", padx=16, pady=(0,4))
    col_hdr = tk.Frame(table_host, bg=CARD); col_hdr.pack(fill="x", pady=(0,2))
    for txt, w in [("Process",8),("Arrival Time",14),("Burst Time",14)]:
        tk.Label(col_hdr, text=txt, bg=CARD, fg=SUBTEXT, font=(MONO,8,"bold"),
                 width=w, anchor="w", padx=8, pady=6).pack(side="left")
    entry_rows = []

    def _build(n):
        for w in table_host.winfo_children()[1:]: w.destroy()
        entry_rows.clear()
        for i in range(n):
            row = tk.Frame(table_host, bg=PANEL if i%2==0 else CARD); row.pack(fill="x", pady=1)
            tk.Label(row, text=f"P{i+1}", bg=row["bg"], fg=ACCENT_G,
                     font=(MONO,10,"bold"), width=8, anchor="w", padx=8).pack(side="left")
            es = []
            for _ in range(2):
                e = tk.Entry(row, bg=BORDER, fg=TEXT, insertbackground=ACCENT_G,
                             relief="flat", font=(MONO,10), width=12,
                             highlightthickness=1, highlightcolor=ACCENT_G, highlightbackground=BORDER)
                e.pack(side="left", padx=(0,8), pady=5); es.append(e)
            entry_rows.append(es)

    def _confirm():
        try:
            n=int(count_entry.get())
            if n<1: raise ValueError
        except ValueError: Widgets.error(win,"Process count must be a positive integer."); return
        _build(n); win.set_status(f"{n} processes loaded – fill in times and press RUN")

    def _randomize():
        try:
            n=int(count_entry.get())
            if n<1: raise ValueError
        except ValueError: Widgets.error(win,"Confirm a process count first."); return
        if not entry_rows: _build(n)
        pool = sorted(random.randint(0,10) for _ in range(n))
        for i,(at_e,bt_e) in enumerate(entry_rows):
            at_e.delete(0,"end"); at_e.insert(0,str(pool[i]))
            bt_e.delete(0,"end"); bt_e.insert(0,str(random.randint(1,10)))
        win.set_status("Random values generated – press RUN to simulate")

    Widgets.button(count_bar,"CONFIRM",_confirm,accent=ACCENT_G,width=10).pack(side="left",padx=10)
    Widgets.button(count_bar,"RANDOM",_randomize,accent=ACCENT_Y,width=10).pack(side="left",padx=(0,10))
    h_rule(win.body,BORDER)
    btn_row=tk.Frame(win.body,bg=BG,pady=8); btn_row.pack(fill="x",padx=16)
    section_header(win.body,"OUTPUT",subtitle="gantt chart · process table · performance",accent=ACCENT_G)
    out=Output(Widgets.output_box(win.body,height=32,accent=ACCENT_G))

    def _run():
        if not entry_rows: Widgets.error(win,"Confirm process count first."); return
        arrival,burst=[],[]
        for i,(at_e,bt_e) in enumerate(entry_rows):
            try:
                at=int(at_e.get()); bt=int(bt_e.get())
                if at<0: raise ValueError("Arrival time cannot be negative.")
                if bt<=0: raise ValueError("Burst time must be positive.")
                arrival.append(at); burst.append(bt)
            except ValueError as e: Widgets.error(win,f"P{i+1}: {e}"); return
        _render(out,_run_sjf(len(entry_rows),arrival,burst))
        win.set_status("Simulation complete",color=ACCENT_G)

    def _clear():
        out.clear(); count_entry.delete(0,"end")
        for w in table_host.winfo_children()[1:]: w.destroy()
        entry_rows.clear(); win.set_status("Cleared")

    Widgets.button(btn_row,"▶  RUN",_run,accent=ACCENT_G,width=14).pack(side="left",padx=(0,8))
    Widgets.button(btn_row,"✕  CLEAR",_clear,accent=ACCENT_R,width=12).pack(side="left")
    win.grab_set()


def _render(out, r):
    out.clear(); n=r["process_count"]
    out.line("  GANTT CHART",tag="header"); out.blank()
    bar="  "
    for p in r["gantt_chart"]: bar+=f"│{p:^6}"
    out.line(bar+"│",tag="accent")
    tl="  "
    for t in r["gantt_time"]: tl+=f"{t:<7}"
    out.line(tl,tag="dim"); out.blank(); out.divider()
    out.line("  PROCESS TABLE",tag="header"); out.blank()
    W=[6,14,12,14,14]
    out.table_row("PID","Arrival","Burst","Turnaround","Waiting",widths=W,tag="bold")
    out.divider("─",62,tag="dim")
    for i in range(n):
        out.table_row(f"P{i+1}",r["arrival_time"][i],r["burst_time"][i],
                      r["turnaround_time"][i],r["waiting_time"][i],
                      widths=W,tag="accent" if i%2==0 else None)
    out.divider("─",62,tag="dim")
    out.table_row("Total","","",r["total_turnaround"],r["total_waiting"],widths=W,tag="bold")
    out.blank(); out.divider()
    out.line("  SYSTEM PERFORMANCE",tag="header"); out.blank()
    out.kv("CPU Busy Time",       r["cpu_busy_time"])
    out.kv("CPU Idle Time",       r["cpu_idle_time"])
    out.kv("CPU Utilization (%)", f"{r['cpu_util']:.2f}  [{r['cpu_label']}]")
    out.line(f"    → {r['cpu_meaning']}",tag="dim")
    out.kv("Throughput",          f"{r['throughput']:.4f}  [{r['throughput_label']}]")
    out.line(f"    → {r['throughput_meaning']}",tag="dim")
    out.kv("Avg Waiting Time",    f"{r['avg_waiting_time']:.2f}")
    out.kv("Avg Turnaround Time", f"{r['avg_turnaround_time']:.2f}")
    out.blank()

if __name__ == "__main__":
    root=tk.Tk(); root.withdraw(); sjf_gui(); root.mainloop()