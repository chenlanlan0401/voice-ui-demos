#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新诉求:给"需要思考的题"配一句思考提示(缓解紧张,不改收音)。
标准回到最朴素的"慢答者占比"——有多少人开口>5秒(需要时间)。
不再看长答率/题内递增(那是给"等待窗口"用的,提示不需要)。
额外:提示场景下,还可以看"多久才算需要提示"——用慢答者的开口分布定提示措辞。
"""
import openpyxl, json
from collections import defaultdict
import statistics

SLOW_SEC=5.0
wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
recs=defaultdict(list); title={}
for r in ws.iter_rows(min_row=2,values_only=True):
    k=f"{r[0]}-{r[1]}"
    recs[k].append((float(r[4]),int(r[5])))
    title[k]=str(r[2])

def pct(vals,p):
    vals=sorted(vals)
    if not vals: return 0
    idx=(len(vals)-1)*p; lo=int(idx); hi=min(lo+1,len(vals)-1)
    return vals[lo]+(vals[hi]-vals[lo])*(idx-lo)

rows=[]
for k,rs in recs.items():
    n=len(rs)
    secs=[s for s,w in rs]
    slow=[s for s in secs if s>SLOW_SEC]
    slow_share=len(slow)/n*100
    # 开口时间分位(全体),看这题整体"需要多久"
    med_all=pct(secs,0.5)
    p75_all=pct(secs,0.75)
    rows.append({"k":k,"title":title[k],"n":n,
        "slow_share":round(slow_share,1),
        "med_all":round(med_all,1),"p75_all":round(p75_all,1),
        "n_slow":len(slow)})

rows.sort(key=lambda x:-x["slow_share"])
print("按【慢答者占比】排序 —— 需要思考的人越多,越该给思考提示")
print("="*88)
print(f"{'题号':<11}{'慢答占比%':>9}{'慢答人数':>8}{'全体开口中位':>12}{'P75':>6}  题目")
print("-"*88)
for r in rows:
    print(f"{r['k']:<11}{r['slow_share']:>9}{r['n_slow']:>8}{r['med_all']:>11}s{r['p75_all']:>5}s  {r['title'][:20]}")

# 找断层
shares=[r["slow_share"] for r in rows]
print("\n慢答占比降序,相邻断层:")
for i in range(1,len(shares)):
    gap=shares[i-1]-shares[i]
    mark=" <=== 明显断层" if gap>=5 else ""
    print(f"  {shares[i-1]:>5} → {shares[i]:>5}  (差{gap:.1f}){mark}")

json.dump(rows,open("/Users/kanyun/voice-ui-demos/hint_data.json","w"),ensure_ascii=False)
