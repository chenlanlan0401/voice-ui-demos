#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核实：总览里的「长答占比」到底是不是"慢的人里的长答比例"（条件指标），
还是全体字数镜像。用慢答原话抽样(45条真实慢答学生)按题分组反算。"""
import openpyxl
from collections import defaultdict
wb = openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-data.xlsx", data_only=True)

# 总览的长答占比（真值）
ws = wb["15题总览"]
ov = {}
for r in ws.iter_rows(min_row=2, values_only=True):
    key=(r[0],r[1])
    ov[key]={"title":str(r[3])[:16],"type":r[2],"slow":float(r[5]),
             "short":float(r[6]),"long":float(r[7]),"cls":r[10]}

# 慢答原话抽样：按题统计 长/短 标签
ws2 = wb["慢答原话抽样"]
samp = defaultdict(lambda:{"long":0,"short":0,"chars":[]})
for r in ws2.iter_rows(min_row=2, values_only=True):
    key=(r[0],r[1])
    label=str(r[7])  # 长/短
    chars=r[6]
    if label=="长": samp[key]["long"]+=1
    elif label=="短": samp[key]["short"]+=1
    if chars is not None: samp[key]["chars"].append(chars)

print("题号-小问 | 类型 | 总览长答占比 | 抽样慢答者长答比 | 抽样n | 抽样字数 | 判类")
print("-"*95)
for key,o in sorted(ov.items(), key=lambda x:-x[1]["long"]):
    s=samp.get(key)
    if s and (s["long"]+s["short"])>0:
        tot=s["long"]+s["short"]
        ratio=s["long"]/tot*100
        chars=sorted(s["chars"])
        cs=f"{min(chars)}~{max(chars)}" if chars else "-"
        print(f"{key[0]}-{key[1]} | {o['type']:<8} | {o['long']:>5.1f}% | "
              f"{ratio:>5.1f}%(={s['long']}/{tot}) | {tot:>2} | {cs:>9} | {o['cls']}")
    else:
        print(f"{key[0]}-{key[1]} | {o['type']:<8} | {o['long']:>5.1f}% | 无抽样        |  0 |         - | {o['cls']}")

print("\n判读：若「抽样慢答者长答比」与「总览长答占比」方向一致(高对高、低对低)，")
print("     则证明长答占比确实是'慢的人里的长答比例'(条件指标)，是真第二轴，")
print("     我之前说的'全体字数镜像'就是错的。")
