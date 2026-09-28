#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证:15题里有没有"慢答人数少但长答率虚高"的题,以及长答率的置信区间。"""
import openpyxl, math
from collections import defaultdict

SLOW_SEC=5.0; LONG_CHARS=15
wb = openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx", data_only=True)
ws = wb["作答明细"]

recs=defaultdict(list)
for r in ws.iter_rows(min_row=2, values_only=True):
    qid,sub,title,sid,sec,words,txt=r
    recs[(str(qid),str(sub))].append((float(sec),int(words),str(title)))

def wilson(p, n, z=1.96):
    """Wilson 置信区间,小样本比率的可信范围。"""
    if n==0: return (0,0)
    denom=1+z*z/n
    center=(p+z*z/(2*n))/denom
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return (max(0,center-half), min(1,center+half))

rows=[]
for key,rs in recs.items():
    n=len(rs); title=rs[0][2]
    slow=[(s,w) for s,w,t in rs if s>SLOW_SEC]
    n_slow=len(slow)
    slow_long=[x for x in slow if x[1]>=LONG_CHARS]
    p=len(slow_long)/n_slow if n_slow else 0
    lo,hi=wilson(p,n_slow)
    rows.append({"key":f"{key[0]}-{key[1]}","title":title[:14],"n":n,
        "n_slow":n_slow,"slow_share":round(n_slow/n*100,1),
        "cond_long":round(p*100,1),"ci_lo":round(lo*100,1),"ci_hi":round(hi*100,1),
        "ci_width":round((hi-lo)*100,1),"misfire":round(len(slow_long)/n*100,1)})

rows.sort(key=lambda x:-x["cond_long"])
print(f"{'题':<11}{'慢答人数':>7}{'慢答%':>6}{'长答率%':>7}{'置信区间95%':>16}{'区间宽':>6}  题目")
print("-"*90)
for r in rows:
    flag=""
    if r["n_slow"]<100: flag+=" ⚠小样本(<100)"
    if r["ci_width"]>25: flag+=" ⚠区间宽"
    print(f"{r['key']:<11}{r['n_slow']:>7}{r['slow_share']:>6}{r['cond_long']:>7}"
          f"{('['+str(r['ci_lo'])+'~'+str(r['ci_hi'])+']'):>16}{r['ci_width']:>6}  {r['title']}{flag}")

print("\n判读:")
print("- 慢答人数<100 且 长答率高 = 我担心的'小样本假高',裸用B会被它骗进来")
print("- 置信区间宽(>25个点) = 这个长答率不可信,换个班可能大变")
