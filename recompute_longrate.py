#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重算:长答率改为全体学生中回答>=15字的占比(不再只看慢答者)。"""
import openpyxl, re, json
from collections import defaultdict

wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
recs=defaultdict(list); title={}
for r in ws.iter_rows(min_row=2,values_only=True):
    k=f"{r[0]}-{r[1]}"
    recs[k].append({"sec":float(r[4]),"w":int(r[5]),"txt":str(r[6] or "")})
    title[k]=str(r[2])

# 无措判定(沿用修正版)
GIVEUP=["不知道","不会","不清楚","忘了","没想好","想不出","不懂","不晓得","没想到","我不"]
def rep_score(t):
    t=re.sub(r"[，。！？、\s]","",t)
    return sum(1 for i in range(len(t)-3) if t[i:i+2]==t[i+2:i+4])
def is_hes(txt,w):
    t=txt.strip()
    if not t: return False
    core=re.sub(r"[，。！？、\s]","",t)
    if core and all(c in "嗯呃啊哦额呐呢" for c in core): return True
    if any(g in t for g in GIVEUP) and w<=15: return True
    if w>=6 and rep_score(t)>=max(4,w*0.25): return True
    stripped=re.sub(r"^[嗯呃啊哦额呢吧，。！？\s]+","",t)
    sc=re.sub(r"[，。！？、\s]","",stripped)
    if len(sc)==0: return True
    if len(sc)<=1 and sc in set("嗯呃啊哦额呐呢吧的了"): return True
    return False

rows=[]
for k,rs in recs.items():
    n=len(rs)
    slow=sum(1 for r in rs if r["sec"]>5)
    long_all=sum(1 for r in rs if r["w"]>=15)     # 全体长答
    hes=sum(1 for r in rs if is_hes(r["txt"],r["w"]))
    rows.append({"k":k,"title":title[k],"n":n,
        "slow_share":round(slow/n*100,1),
        "long_all":round(long_all/n*100,1),      # 新:全体长答率
        "hes_rate":round(hes/n*100,1)})
json.dump(rows,open("/Users/kanyun/voice-ui-demos/signals_v2.json","w"),ensure_ascii=False)
for r in sorted(rows,key=lambda x:-x["slow_share"]):
    print(f"{r['k']} {r['title'][:14]:<15} 慢答{r['slow_share']:>5} 全体长答{r['long_all']:>5} 无措{r['hes_rate']:>5}")
