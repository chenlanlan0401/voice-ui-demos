#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为双口径报告备齐所有数字，输出 report_data.json。"""
import openpyxl, json
from collections import defaultdict

SLOW_SEC=5.0; LONG_CHARS=15

wb = openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx", data_only=True)
ws = wb["作答明细"]
wb2 = openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-data.xlsx", data_only=True)
qtype={}
for r in wb2["15题总览"].iter_rows(min_row=2, values_only=True):
    qtype[(str(r[0]),str(r[1]))]=r[2]

rows=defaultdict(list)
allsec=[]
for r in ws.iter_rows(min_row=2, values_only=True):
    qid,sub,title,sid,sec,words,txt=r
    rows[(str(qid),str(sub))].append((float(sec),int(words)))
    allsec.append(float(sec))

def pct(vals,p):
    vals=sorted(vals)
    if not vals: return 0
    idx=(len(vals)-1)*p; lo=int(idx); hi=min(lo+1,len(vals)-1)
    return vals[lo]+(vals[hi]-vals[lo])*(idx-lo)

table=[]
for key,recs in rows.items():
    n=len(recs)
    slow=[(s,w) for s,w in recs if s>SLOW_SEC]
    n_slow=len(slow)
    slow_share=n_slow/n
    slow_long=[(s,w) for s,w in slow if w>=LONG_CHARS]
    cond_long=len(slow_long)/n_slow if n_slow else 0
    misfire=len(slow_long)/n
    ss=[s for s,w in slow]
    table.append({
        "qid":key[0],"sub":key[1],"type":qtype.get(key,"?"),"n":n,
        "title":wb2["15题总览"] and next((str(r[3]) for r in wb2["15题总览"].iter_rows(min_row=2,values_only=True) if str(r[0])==key[0] and str(r[1])==key[1]),""),
        "slow_share":round(slow_share*100,1),
        "cond_long":round(cond_long*100,1),
        "misfire":round(misfire*100,1),
        "n_slow":n_slow,"n_slowlong":len(slow_long),
        "med":round(pct(ss,0.5),1) if ss else 0,
        "p75":round(pct(ss,0.75),1) if ss else 0,
        "p90":round(pct(ss,0.90),1) if ss else 0,
        # 全体开口分布(用于秒数权衡曲线)：每秒累计开口率
        "cum":[round(sum(1 for s,w in recs if s<=t)/n*100,1) for t in range(0,21)],
        # 慢答者里长答者的开口秒数(用于"多等X秒能救多少长答学生")
        "slowlong_secs":sorted([round(s,1) for s,w in slow_long]),
    })

table.sort(key=lambda x:-x["misfire"])
out={"params":{"slow_sec":SLOW_SEC,"long_chars":LONG_CHARS},
     "meta":{"students":len(set()),"records":len(allsec),
             "all_median_sec":round(sorted(allsec)[len(allsec)//2],1)},
     "table":table}
with open("/Users/kanyun/voice-ui-demos/report_data.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False)
print("已生成 report_data.json,题数",len(table))
for t in table:
    print(f"  {t['qid']}-{t['sub']} 慢{t['slow_share']}% 慢长{t['cond_long']}% 误伤{t['misfire']}% P75={t['p75']}s")
