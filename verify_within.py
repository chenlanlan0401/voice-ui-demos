#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题内验证:开口时间是否"买到了"更多内容。
对每道题,把学生按开口秒数分档,看各档中位字数。
- 该等:开口越慢,字数越高(递增)=多给时间转化成了内容
- 不该等:平坦或倒挂=多给时间没用(卡壳)
用它独立验证之前的"该等/不该等"判定。
"""
import openpyxl, json
from collections import defaultdict
import statistics

wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
recs=defaultdict(list)
title={}
for r in ws.iter_rows(min_row=2,values_only=True):
    k=f"{r[0]}-{r[1]}"
    recs[k].append((float(r[4]),int(r[5])))
    title[k]=str(r[2])

# 之前的最终判定
final=json.load(open("/Users/kanyun/voice-ui-demos/final_verdict.json"))
verdict={f["key"]:f["verdict"] for f in final}
misfire={f["key"]:f["misfire"] for f in final}

# 分档:开口秒数区间
bands=[(0,3),(3,5),(5,8),(8,15),(15,999)]
blab=["0-3s","3-5s","5-8s","8-15s","15s+"]

def med(xs): return statistics.median(xs) if xs else 0

print("题内验证:各开口时段的【中位回答字数】(看是否随开口变慢而递增)")
print("="*100)
rows=[]
for k in sorted(recs, key=lambda x:-misfire[x]):
    rs=recs[k]
    cells=[]
    for lo,hi in bands:
        ws_=[w for s,w in rs if lo<=s<hi]
        cells.append((len(ws_), med(ws_)))
    # 判断趋势:比较慢档(5s+)和快档(3-5s)的中位字数
    fast_med = med([w for s,w in rs if 3<=s<5])
    slow_med = med([w for s,w in rs if 5<=s<15])
    trend = "↑递增" if slow_med > fast_med*1.15 else ("↓倒挂" if slow_med < fast_med*0.85 else "→平坦")
    consistent = ("✓一致" if (verdict[k]=="该等" and trend=="↑递增") or (verdict[k]=="不该等" and trend!="↑递增") else "✗打架")
    rows.append({"k":k,"verdict":verdict[k],"misfire":misfire[k],
                 "fast_med":fast_med,"slow_med":slow_med,"trend":trend,"consistent":consistent,
                 "cells":cells})
    cellstr=" | ".join(f"{blab[i]}:{c[1]:.0f}字(n{c[0]})" for i,c in enumerate(cells))
    print(f"\n[{verdict[k]}] {k} 误伤{misfire[k]}% {trend} {consistent}  {title[k][:16]}")
    print(f"    {cellstr}")

print("\n"+"="*100)
print("小结:")
agree=sum(1 for r in rows if r["consistent"]=="✓一致")
print(f"  题内验证与判定一致: {agree}/{len(rows)} 道")
print("  打架的题(需重新看):")
for r in rows:
    if r["consistent"]=="✗打架":
        print(f"    {r['k']} 判定[{r['verdict']}] 但趋势[{r['trend']}] (快档{r['fast_med']:.0f}字 vs 慢档{r['slow_med']:.0f}字)")

json.dump(rows,open("/Users/kanyun/voice-ui-demos/within_verify.json","w"),ensure_ascii=False)
