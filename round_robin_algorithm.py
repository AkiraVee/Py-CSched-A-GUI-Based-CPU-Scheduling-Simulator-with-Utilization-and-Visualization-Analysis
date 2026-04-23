import tkinter as tk
import random
from theme import (
    AlgoWindow, Widgets, Output, section_header, h_rule,
    ACCENT_B, ACCENT_R, ACCENT_Y, BG, PANEL, CARD, BORDER, TEXT, SUBTEXT, MONO
)


def _perf_labels(cpu_util, throughput):
    if cpu_util < 40:    cpu_label, cpu_meaning = "Poor",     "CPU is mostly idle (underutilized)."
    elif cpu_util < 70:  cpu_label, cpu_meaning = "Fair",     "Moderate CPU usage."
    elif cpu_util <= 90: cpu_label, cpu_meaning = "Good",     "Efficient CPU usage."
    else:                cpu_label, cpu_meaning = "High",     "Very high CPU load."
    if throughput < 0.5: tp_label,  tp_meaning  = "Low",      "Few processes completed."
    elif throughput <= 1:tp_label,  tp_meaning  = "Moderate", "Balanced completion rate."
    else:                tp_label,  tp_meaning  = "High",     "Fast process completion."
    return cpu_label, cpu_meaning, tp_label, tp_meaning


def _run_rr(process_count, arrival_time, burst_time, time_quantum):
    remaining_burst=burst_time.copy(); start_time=[-1]*process_count; finish_time=[0]*process_count
    current_time=0; queue=[]; completed=0; cpu_idle_time=0
    entered=[False]*process_count; gantt_chart=[]
    while completed < process_count:
        for i in range(process_count):
            if arrival_time[i]<=current_time and not entered[i]:
                queue.append(i); entered[i]=True
        if not queue:
            start=current_time; current_time+=1; cpu_idle_time+=1; end=current_time
            if gantt_chart and gantt_chart[-1][0]=="ID" and gantt_chart[-1][2]==start:
                gantt_chart[-1]=("ID",gantt_chart[-1][1],end)
            else: gantt_chart.append(("ID",start,end))
            continue
        current=queue.pop(0)
        if start_time[current]==-1: start_time[current]=current_time
        execute_time=min(time_quantum,remaining_burst[current])
        start=current_time; current_time+=execute_time; remaining_burst[current]-=execute_time; end=current_time
        label=f"P{current+1}"
        if gantt_chart and gantt_chart[-1][0]==label and gantt_chart[-1][2]==start:
            gantt_chart[-1]=(label,gantt_chart[-1][1],end)
        else: gantt_chart.append((label,start,end))
        for i in range(process_count):
            if arrival_time[i]<=current_time and not entered[i]:
                queue.append(i); entered[i]=True
        if remaining_burst[current]>0: queue.append(current)
        else: finish_time[current]=current_time; completed+=1
    turnaround_time=[]; waiting_time=[]; total_turnaround=0; total_waiting=0
    for i in range(process_count):
        tat=finish_time[i]-arrival_time[i]; wt=tat-burst_time[i]
        turnaround_time.append(tat); waiting_time.append(wt)
        total_turnaround+=tat; total_waiting+=wt
    cpu_busy_time=sum(burst_time); total_time=gantt_chart[-1][2]
    cpu_util=(cpu_busy_time/total_time)*100; throughput=process_count/total_time
    cpu_label,cpu_meaning,tp_label,tp_meaning=_perf_labels(cpu_util,throughput)
    return dict(
        process_count=process_count, arrival_time=arrival_time,
        burst_time=burst_time, time_quantum=time_quantum,
        turnaround_time=turnaround_time, waiting_time=waiting_time,
        total_turnaround=total_turnaround, total_waiting=total_waiting,
        gantt_chart=gantt_chart, cpu_busy_time=cpu_busy_time,
        cpu_idle_time=cpu_idle_time, cpu_utilization=cpu_util,
        throughput=throughput, avg_waiting_time=total_waiting/process_count,
        avg_turnaround_time=total_turnaround/process_count,
        cpu_label=cpu_label, cpu_meaning=cpu_meaning,
        throughput_label=tp_label, throughput_meaning=tp_meaning,
    )


def round_robin_gui():
    win = AlgoWindow("Round Robin  –  Preemptive", accent=ACCENT_B, width=800, height=700)

    section_header(win.body,"STEP 1  –  PROCESS COUNT",accent=ACCENT_B)
    count_bar,count_entry=Widgets.count_bar(win.body,"Number of processes")
    count_bar.pack(fill="x",padx=16,pady=(4,2))
    h_rule(win.body,BORDER)

    section_header(win.body,"STEP 2  –  TIME QUANTUM",accent=ACCENT_B)
    tq_bar=tk.Frame(win.body,bg=PANEL,padx=16,pady=10); tq_bar.pack(fill="x")
    tk.Label(tq_bar,text="Time quantum",bg=PANEL,fg=SUBTEXT,font=(MONO,10)).pack(side="left")
    tq_entry=tk.Entry(tq_bar,bg=BORDER,fg=TEXT,insertbackground=ACCENT_B,
                      relief="flat",font=(MONO,10),width=5,
                      highlightthickness=1,highlightcolor=ACCENT_B,highlightbackground=BORDER)
    tq_entry.pack(side="left",padx=10)
    h_rule(win.body,BORDER)

    section_header(win.body,"STEP 3  –  ARRIVAL & BURST TIMES",accent=ACCENT_B)
    table_host=tk.Frame(win.body,bg=BG); table_host.pack(fill="x",padx=16,pady=(0,4))
    col_hdr=tk.Frame(table_host,bg=CARD); col_hdr.pack(fill="x",pady=(0,2))
    for txt,w in [("Process",8),("Arrival Time",14),("Burst Time",14)]:
        tk.Label(col_hdr,text=txt,bg=CARD,fg=SUBTEXT,font=(MONO,8,"bold"),
                 width=w,anchor="w",padx=8,pady=6).pack(side="left")
    entry_rows=[]

    def _build(n):
        for w in table_host.winfo_children()[1:]: w.destroy()
        entry_rows.clear()
        for i in range(n):
            row=tk.Frame(table_host,bg=PANEL if i%2==0 else CARD); row.pack(fill="x",pady=1)
            tk.Label(row,text=f"P{i+1}",bg=row["bg"],fg=ACCENT_B,
                     font=(MONO,10,"bold"),width=8,anchor="w",padx=8).pack(side="left")
            es=[]
            for _ in range(2):
                e=tk.Entry(row,bg=BORDER,fg=TEXT,insertbackground=ACCENT_B,
                           relief="flat",font=(MONO,10),width=12,
                           highlightthickness=1,highlightcolor=ACCENT_B,highlightbackground=BORDER)
                e.pack(side="left",padx=(0,8),pady=5); es.append(e)
            entry_rows.append(es)

    def _confirm():
        try:
            n=int(count_entry.get())
            if n<1: raise ValueError
        except ValueError: Widgets.error(win,"Process count must be a positive integer."); return
        _build(n); win.set_status(f"{n} processes loaded")

    def _randomize():
        try:
            n=int(count_entry.get())
            if n<1: raise ValueError
        except ValueError: Widgets.error(win,"Confirm a process count first."); return
        if not entry_rows: _build(n)
        if not tq_entry.get():
            tq_entry.insert(0,str(random.randint(1,5)))
        pool=sorted(random.randint(0,10) for _ in range(n))
        for i,(at_e,bt_e) in enumerate(entry_rows):
            at_e.delete(0,"end"); at_e.insert(0,str(pool[i]))
            bt_e.delete(0,"end"); bt_e.insert(0,str(random.randint(1,10)))
        win.set_status("Random values generated – press RUN to simulate")

    Widgets.button(count_bar,"CONFIRM",_confirm,accent=ACCENT_B,width=10).pack(side="left",padx=10)
    Widgets.button(count_bar,"RANDOM",_randomize,accent=ACCENT_Y,width=10).pack(side="left",padx=(0,10))
    h_rule(win.body,BORDER)
    btn_row=tk.Frame(win.body,bg=BG,pady=8); btn_row.pack(fill="x",padx=16)
    section_header(win.body,"OUTPUT",subtitle="gantt chart · process table · performance",accent=ACCENT_B)
    out=Output(Widgets.output_box(win.body,height=16,accent=ACCENT_B))

    def _run():
        if not entry_rows: Widgets.error(win,"Confirm process count first."); return
        try:
            tq=int(tq_entry.get())
            if tq<=0: raise ValueError("Time quantum must be positive.")
        except ValueError as e: Widgets.error(win,str(e)); return
        arrival,burst=[],[]
        for i,(at_e,bt_e) in enumerate(entry_rows):
            try:
                at=int(at_e.get()); bt=int(bt_e.get())
                if at<0: raise ValueError("Arrival time cannot be negative.")
                if bt<=0: raise ValueError("Burst time must be positive.")
                arrival.append(at); burst.append(bt)
            except ValueError as e: Widgets.error(win,f"P{i+1}: {e}"); return
        _render(out,_run_rr(len(entry_rows),arrival,burst,tq))
        win.set_status("Simulation complete",color=ACCENT_B)

    def _clear():
        out.clear(); count_entry.delete(0,"end"); tq_entry.delete(0,"end")
        for w in table_host.winfo_children()[1:]: w.destroy()
        entry_rows.clear(); win.set_status("Cleared")

    Widgets.button(btn_row,"▶  RUN",_run,accent=ACCENT_B,width=14).pack(side="left",padx=(0,8))
    Widgets.button(btn_row,"✕  CLEAR",_clear,accent=ACCENT_R,width=12).pack(side="left")
    win.grab_set()


def _render(out,r):
    out.clear(); n=r["process_count"]
    out.line(f"  GANTT CHART   (quantum = {r['time_quantum']})",tag="header"); out.blank()
    bar="  "
    for g in r["gantt_chart"]: bar+=f"│{g[0]:^6}"
    out.line(bar+"│",tag="accent")
    tl="  "
    for g in r["gantt_chart"]: tl+=f"{g[1]:<7}"
    tl+=str(r["gantt_chart"][-1][2])
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
    out.kv("CPU Utilization (%)", f"{r['cpu_utilization']:.2f}  [{r['cpu_label']}]")
    out.line(f"    → {r['cpu_meaning']}",tag="dim")
    out.kv("Throughput",          f"{r['throughput']:.4f}  [{r['throughput_label']}]")
    out.line(f"    → {r['throughput_meaning']}",tag="dim")
    out.kv("Avg Waiting Time",    f"{r['avg_waiting_time']:.2f}")
    out.kv("Avg Turnaround Time", f"{r['avg_turnaround_time']:.2f}")
    out.blank()

if __name__ == "__main__":
    root=tk.Tk(); root.withdraw(); round_robin_gui(); root.mainloop()