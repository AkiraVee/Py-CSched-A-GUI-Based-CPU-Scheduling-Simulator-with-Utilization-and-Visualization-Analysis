"""
pre_priosched_algorithm.py  –  Priority Scheduling (Preemptive)
Logic unchanged. GUI added via theme.py.
"""
import tkinter as tk
from theme import (
    AlgoWindow, Widgets, Output, section_header, h_rule,
    ACCENT_B, ACCENT_R, BG, PANEL, CARD, BORDER, TEXT, SUBTEXT, MONO
)


# ── pure logic ────────────────────────────────────────────
def _run_pp(n, arrival, burst, priority):
    remaining=burst[:]; completed=[False]*n; start=[-1]*n; finish=[0]*n
    time=0; done=0; gantt=[]; last=None

    while done < n:
        idx=-1; best=float("inf")
        for i in range(n):
            if arrival[i]<=time and remaining[i]>0:
                if priority[i]<best: best=priority[i]; idx=i
        if idx==-1:
            if gantt and gantt[-1][0]=="ID": gantt[-1][2]+=1
            else: gantt.append(["ID",time,time+1])
            time+=1; last="ID"; continue
        label=f"P{idx+1}"
        if start[idx]==-1: start[idx]=time
        if gantt and gantt[-1][0]==label: gantt[-1][2]+=1
        else: gantt.append([label,time,time+1])
        remaining[idx]-=1; time+=1
        if remaining[idx]==0: finish[idx]=time; completed[idx]=True; done+=1

    total_tat=0; total_wt=0; turnaround_time=[]; waiting_time=[]
    for i in range(n):
        tat=finish[i]-arrival[i]; wt=tat-burst[i]
        turnaround_time.append(tat); waiting_time.append(wt)
        total_tat+=tat; total_wt+=wt

    cpu_busy=sum(burst); total_time=time
    return dict(
        n=n, arrival=arrival, burst=burst, priority=priority,
        turnaround_time=turnaround_time, waiting_time=waiting_time,
        total_tat=total_tat, total_wt=total_wt, gantt=gantt,
        cpu_busy=cpu_busy, cpu_idle=total_time-cpu_busy,
        util=(cpu_busy/total_time)*100, throughput=n/total_time,
        avg_wt=total_wt/n, avg_tat=total_tat/n,
    )


# ── gui ───────────────────────────────────────────────────
def priority_preemptive_gui():
    win = AlgoWindow("Priority Scheduling  –  Preemptive", accent=ACCENT_B, width=860, height=680)

    section_header(win.body, "STEP 1  –  PROCESS COUNT", accent=ACCENT_B)
    count_bar, count_entry = Widgets.count_bar(win.body, "Number of processes")
    count_bar.pack(fill="x", padx=16, pady=(4,2))
    h_rule(win.body, BORDER)

    section_header(win.body, "STEP 2  –  ARRIVAL, BURST & PRIORITY", accent=ACCENT_B)
    tk.Label(win.body, text="  Lower priority number = higher priority",
             bg=BG, fg=SUBTEXT, font=(MONO,8), anchor="w").pack(fill="x", padx=16)

    table_host=tk.Frame(win.body,bg=BG); table_host.pack(fill="x",padx=16,pady=(4,4))
    col_hdr=tk.Frame(table_host,bg=CARD); col_hdr.pack(fill="x",pady=(0,2))
    for txt,w in [("Process",8),("Arrival",12),("Burst",12),("Priority",10)]:
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
            for _ in range(3):
                e=tk.Entry(row,bg=BORDER,fg=TEXT,insertbackground=ACCENT_B,
                           relief="flat",font=(MONO,10),width=10,
                           highlightthickness=1,highlightcolor=ACCENT_B,highlightbackground=BORDER)
                e.pack(side="left",padx=(0,8),pady=5); es.append(e)
            entry_rows.append(es)

    def _confirm():
        try:
            n=int(count_entry.get())
            if n<1: raise ValueError
        except ValueError: Widgets.error(win,"Process count must be a positive integer."); return
        _build(n); win.set_status(f"{n} processes loaded")

    Widgets.button(count_bar,"CONFIRM",_confirm,accent=ACCENT_B,width=10).pack(side="left",padx=10)
    h_rule(win.body,BORDER)
    btn_row=tk.Frame(win.body,bg=BG,pady=8); btn_row.pack(fill="x",padx=16)
    section_header(win.body,"OUTPUT",subtitle="gantt chart · process table · performance",accent=ACCENT_B)
    out=Output(Widgets.output_box(win.body,height=16,accent=ACCENT_B))

    def _run():
        if not entry_rows: Widgets.error(win,"Confirm process count first."); return
        arrival,burst,prio=[],[],[]
        for i,(at_e,bt_e,pr_e) in enumerate(entry_rows):
            try:
                at=int(at_e.get()); bt=int(bt_e.get()); pr=int(pr_e.get())
                if at<0: raise ValueError("Arrival time cannot be negative.")
                if bt<=0: raise ValueError("Burst time must be positive.")
                arrival.append(at); burst.append(bt); prio.append(pr)
            except ValueError as e: Widgets.error(win,f"P{i+1}: {e}"); return
        r=_run_pp(len(entry_rows),arrival,burst,prio); _render(out,r)
        win.set_status("Simulation complete", color=ACCENT_B)

    def _clear():
        out.clear(); count_entry.delete(0,"end")
        for w in table_host.winfo_children()[1:]: w.destroy()
        entry_rows.clear(); win.set_status("Cleared")

    Widgets.button(btn_row,"▶  RUN",_run,accent=ACCENT_B,width=14).pack(side="left",padx=(0,8))
    Widgets.button(btn_row,"✕  CLEAR",_clear,accent=ACCENT_R,width=12).pack(side="left")
    win.grab_set()


def _render(out, r):
    out.clear(); n=r["n"]
    out.line("  GANTT CHART", tag="header"); out.blank()
    bar="  "
    for g in r["gantt"]: bar+=f"│{g[0]:^6}"
    out.line(bar+"│", tag="accent")
    tl="  "
    for g in r["gantt"]: tl+=f"{g[1]:<7}"
    tl+=str(r["gantt"][-1][2])
    out.line(tl, tag="dim"); out.blank(); out.divider()
    out.line("  PROCESS TABLE", tag="header"); out.blank()
    W=[6,12,10,10,12,12]
    out.table_row("PID","Arrival","Burst","Priority","Turnaround","Waiting",widths=W,tag="bold")
    out.divider("─",64,tag="dim")
    for i in range(n):
        out.table_row(f"P{i+1}",r["arrival"][i],r["burst"][i],
                      r["priority"][i],r["turnaround_time"][i],r["waiting_time"][i],
                      widths=W,tag="accent" if i%2==0 else None)
    out.divider("─",64,tag="dim")
    out.table_row("Total","","","",r["total_tat"],r["total_wt"],widths=W,tag="bold")
    out.blank(); out.divider()
    out.line("  SYSTEM PERFORMANCE", tag="header"); out.blank()
    out.kv("CPU Busy Time",       r["cpu_busy"])
    out.kv("CPU Idle Time",       r["cpu_idle"])
    out.kv("CPU Utilization (%)", f"{r['util']:.2f}")
    out.kv("Throughput",          f"{r['throughput']:.4f}")
    out.kv("Avg Waiting Time",    f"{r['avg_wt']:.2f}")
    out.kv("Avg Turnaround Time", f"{r['avg_tat']:.2f}")
    out.blank()


if __name__ == "__main__":
    root=tk.Tk(); root.withdraw(); priority_preemptive_gui(); root.mainloop()