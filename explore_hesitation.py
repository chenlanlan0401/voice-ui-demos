#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探索无措信号:看回答原文里"不知道说啥"长什么样。"""
import openpyxl, re
from collections import defaultdict

wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
rows=[]
for r in ws.iter_rows(min_row=2,values_only=True):
    rows.append({"q":f"{r[0]}-{r[1]}","sec":float(r[4]),"w":int(r[5]),"txt":str(r[6] or "")})

print(f"总 {len(rows)} 条")

# 1) 看开口填充词/无措开头的分布
fillers=["嗯","呃","啊","这个","那个","不知道","我不会","我忘了","不清楚","没有","忘了"]
print("\n=== 以填充词/无措词开头 或 极短无实质 的样本(随机看) ===")
cnt=0
for r in rows:
    t=r["txt"].strip()
    if not t: continue
    # 无措候选:很短且以填充词开头,或整句就是填充
    head=t[:3]
    if (r["w"]<=8 and any(t.startswith(f) for f in fillers)) and cnt<15:
        print(f"  [{r['q']}] {r['sec']}s/{r['w']}字: {t[:40]}")
        cnt+=1

# 2) 重复/结巴特征:连续重复的字或词
print("\n=== 疑似重复结巴(同一2-3字短串连续出现) ===")
def rep_score(t):
    # 数连续重复的2字串
    reps=0
    for i in range(len(t)-3):
        if t[i:i+2]==t[i+2:i+4]:
            reps+=1
    return reps
cnt=0
for r in rows:
    t=r["txt"]
    if r["w"]>=20 and rep_score(t)>=3 and cnt<12:
        print(f"  [{r['q']}] {r['sec']}s/{r['w']}字 rep={rep_score(t)}: {t[:50]}")
        cnt+=1

# 3) 反问/答非所问信号:回答里带大量问号(把问题又抛回来)
print("\n=== 回答里带问号(可能是没理解、反问、复读题目) ===")
cnt=0
for r in rows:
    t=r["txt"]
    qmarks=t.count("?")+t.count("？")
    if qmarks>=2 and cnt<10:
        print(f"  [{r['q']}] {r['sec']}s/{r['w']}字 问号x{qmarks}: {t[:50]}")
        cnt+=1
