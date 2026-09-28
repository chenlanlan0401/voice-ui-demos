#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证:chat表createdtime间隔 能否代理 lesson4埋点开口秒数。
思路:取lesson4行级表(有真实开口秒数)的学生,从chat表算AI问->学生答的时间戳间隔,
     两者按题聚合后比相关性。相关性高=路径B可用。
先只探chat时间戳的语义:AI消息时间 vs 学生消息时间 的差,分布是否合理。
"""
import openpyxl,json
wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
# 取每题的真实开口秒数中位,作为对照基准
from collections import defaultdict
byq=defaultdict(list)
for r in ws.iter_rows(min_row=2,values_only=True):
    byq[f"{r[0]}-{r[1]}"].append(float(r[4]))
print("lesson4 各题真实开口秒数中位(埋点口径):")
for k in sorted(byq):
    v=sorted(byq[k])
    print(f"  {k}: 中位{v[len(v)//2]:.1f}s  n={len(v)}")
