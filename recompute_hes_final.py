#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一无措率口径:用收紧口径(有实义短答一律保留)重算每题无措率,
回写 signals_v2.json 和 final_v4.json 的无措字段,不动其他人工列。
假性无措不纳入。
收紧口径 = fake_hesitation_v2.py 的 is_hesitation:放弃词/纯填充/重复结巴三类。
"""
import openpyxl, re, json
from collections import defaultdict

wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
recs=defaultdict(list)
for r in ws.iter_rows(min_row=2,values_only=True):
    recs[f"{r[0]}-{r[1]}"].append({"sec":float(r[4]),"w":int(r[5]),"txt":str(r[6] or "")})

GIVEUP=["不知道","不会","不清楚","忘了","没想好","想不出","不懂","没有了","不晓得","不记得","没想到","想不起"]
def rep_score(t):
    t=re.sub(r"[，。！？、\s]","",t); reps=0
    for i in range(len(t)-3):
        if t[i:i+2]==t[i+2:i+4]: reps+=1
    return reps
def is_hes(txt,w):
    t=txt.strip()
    if not t: return False
    core=re.sub(r"[，。！？、\s~～]","",t)
    if not core: return False
    if all(c in "嗯呃啊哦额呐哈唉" for c in core): return True
    if any(g in t for g in GIVEUP) and w<=15: return True
    if len(core)>=6 and rep_score(t)>=max(4,w*0.25): return True
    return False

hes_rate={}
for k,rs in recs.items():
    h=sum(1 for r in rs if is_hes(r["txt"],r["w"]))
    hes_rate[k]=round(h/len(rs)*100,1)

# 回写 signals_v2.json —— 字段 hes_rate
sig=json.load(open("/Users/kanyun/voice-ui-demos/signals_v2.json"))
print("=== signals_v2.json 无措率变化 ===")
for row in sig:
    old=row.get("hes_rate"); new=hes_rate[row["k"]]
    if old!=new: print(f"  {row['k']:<11} {old:>5} → {new:<5}  {row['title'][:16]}")
    row["hes_rate"]=new
json.dump(sig,open("/Users/kanyun/voice-ui-demos/signals_v2.json","w"),ensure_ascii=False)

# 回写 final_v4.json —— 字段 hes
fv=json.load(open("/Users/kanyun/voice-ui-demos/final_v4.json"))
print("\n=== final_v4.json 无措率变化 ===")
for row in fv:
    old=row.get("hes"); new=hes_rate[row["k"]]
    if old!=new: print(f"  {row['k']:<11} {old:>5} → {new:<5}  {row['title'][:16]}")
    row["hes"]=new
json.dump(fv,open("/Users/kanyun/voice-ui-demos/final_v4.json","w"),ensure_ascii=False)

print("\n两文件无措率已统一为收紧口径。假性无措未纳入。")
