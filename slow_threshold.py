#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""慢答阈值敏感性:开口秒数含1-2秒链路延迟,把阈值从>5秒提到>6/>7秒,
看每题慢答占比怎么变、题目排序会不会翻盘。"""
import openpyxl
from collections import defaultdict

wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
recs=defaultdict(list); title={}
for r in ws.iter_rows(min_row=2,values_only=True):
    k=f"{r[0]}-{r[1]}"; recs[k].append(float(r[4])); title[k]=str(r[2])

rows=[]
for k,secs in recs.items():
    n=len(secs)
    s5=sum(1 for x in secs if x>5)/n*100
    s6=sum(1 for x in secs if x>6)/n*100
    s7=sum(1 for x in secs if x>7)/n*100
    rows.append({"k":k,"t":title[k][:16],"n":n,
        "s5":round(s5,1),"s6":round(s6,1),"s7":round(s7,1),
        "d57":round(s5-s7,1)})

# 按5秒口径排(和现有报告一致),看提门槛后的变化
rows.sort(key=lambda x:-x["s5"])
print(f"{'题号':<11}{'>5秒':>6}{'>6秒':>6}{'>7秒':>6}{'掉幅5→7':>8}  题目")
print("-"*70)
for r in rows:
    print(f"{r['k']:<11}{r['s5']:>6}{r['s6']:>6}{r['s7']:>6}{r['d57']:>8}  {r['t']}")

# 各阈值下的排序,看Top有没有翻盘
print("\n【排序对比】各阈值下慢答Top8")
for th in ["s5","s6","s7"]:
    top=sorted(rows,key=lambda x:-x[th])[:8]
    lab={"s5":">5秒",": ":""}.get(th,th)
    print(f"  {th[1]}秒: "+" ".join(f"{r['k']}({r[th]})" for r in top))

# 整体均值
import statistics as st
for th in ["s5","s6","s7"]:
    print(f"{th[1]}秒 全课慢答均值(题级): {round(st.mean(r[th] for r in rows),1)}%")
