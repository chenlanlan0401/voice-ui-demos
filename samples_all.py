#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15题每道给:完整表现+分档原话样本,供人工判断。"""
import openpyxl, re, json
from collections import defaultdict

wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
recs=defaultdict(list); title={}
for r in ws.iter_rows(min_row=2,values_only=True):
    k=f"{r[0]}-{r[1]}"
    recs[k].append({"sec":float(r[4]),"w":int(r[5]),"txt":str(r[6] or "")})
    title[k]=str(r[2])

sig={x['k']:x for x in json.load(open("signals_v2.json"))}
fv={x['k']:x for x in json.load(open("final_v3.json"))}

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

# 排序:按最终结论
order=['🟢 该等','🟢 该等(中间+数据支持)','🟠 留意','⚪ 不给(用户定:短答题)','⚪ 不用']
keys=sorted(recs.keys(), key=lambda k: order.index(fv[k]['v']) if fv[k]['v'] in order else 99)

out=[]
for k in keys:
    rs=recs[k]
    x=sig[k]; f=fv[k]
    # 分档取样
    fast_long=[r for r in rs if r["sec"]<=3 and r["w"]>=15]      # 快而长
    slow_long=[r for r in rs if r["sec"]>5 and r["w"]>=15]        # 慢而长
    slow_short=[r for r in rs if r["sec"]>5 and r["w"]<15 and not is_hes(r["txt"],r["w"])]  # 慢而短(有效)
    hes=[r for r in rs if is_hes(r["txt"],r["w"])]               # 无措
    def pick(lst,n=3,bylen=False):
        lst=[r for r in lst if r["txt"].strip()]
        if bylen: lst=sorted(lst,key=lambda r:-r["w"])
        return lst[:n]
    out.append({"k":k,"title":title[k],"sig":x,"fv":f,
        "fast_long":pick(fast_long,3,True),
        "slow_long":pick(slow_long,3,True),
        "slow_short":pick(slow_short,3),
        "hes":pick(hes,3)})

# 打印
for o in out:
    x=o["sig"]; f=o["fv"]
    print("="*80)
    print(f"【{f['v']}】{o['k']}  {o['title']}")
    print(f"  耗时分{f['ts']} | 慢答{x['slow_share']}% 全体长答{x['long_all']}% 无措{x['hes_rate']}% | 画像:{f['pf']}")
    if o["fast_long"]:
        print("  ▸ 快答但说得长(≤3秒/≥15字):")
        for r in o["fast_long"]: print(f"      {r['sec']}s/{r['w']}字: {r['txt'][:44]}")
    if o["slow_long"]:
        print("  ▸ 慢答且说得长(>5秒/≥15字):")
        for r in o["slow_long"]: print(f"      {r['sec']}s/{r['w']}字: {r['txt'][:44]}")
    if o["slow_short"]:
        print("  ▸ 慢答但说得短(>5秒/<15字·有效):")
        for r in o["slow_short"]: print(f"      {r['sec']}s/{r['w']}字: {r['txt'][:44]}")
    if o["hes"]:
        print("  ▸ 无措(嗯/呃/不知道/结巴):")
        for r in o["hes"]: print(f"      {r['sec']}s/{r['w']}字: {r['txt'][:44]}")
