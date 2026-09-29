#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把沉默率(questionid级)合并进三信号(小问级),拼成完整漏斗表。
沉默→开口→内容 的完整链路:沉默率 / 慢答 / 长答 / 无措。
沉默率是 questionid 聚合(含1-2小问),同一questionid的小问共享,标注。"""
import json

sig=json.load(open("/Users/kanyun/voice-ui-demos/signals_v2.json"))

# questionid → 沉默率(来自察察查询 25655805)
silent={
 "466973":6.9,"466172":6.8,"466974":5.6,"466169":5.4,"466171":5.2,
 "466168":5.1,"466170":4.8,"398696":4.8,"398695":3.8,"466975":3.6}

rows=[]
for r in sig:
    qid=r["k"].split("-")[0]
    rows.append({
        "k":r["k"],"title":r["title"],
        "silent":silent.get(qid),      # questionid级
        "slow":r["slow_share"],"long":r["long_all"],"hes":r["hes_rate"]})

# 按沉默率排,再按无措
rows.sort(key=lambda x:(-(x["silent"] or 0),-x["hes"]))
json.dump(rows,open("/Users/kanyun/voice-ui-demos/funnel.json","w"),ensure_ascii=False,indent=1)

print(f"{'题号':<10}{'沉默%':>6}{'慢答%':>7}{'长答%':>7}{'无措%':>7}  题目")
print("-"*80)
for r in rows:
    print(f"{r['k']:<10}{r['silent']:>6}{r['slow']:>7}{r['long']:>7}{r['hes']:>7}  {r['title'][:18]}")
