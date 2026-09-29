#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""四象限数据 + 无措判定自检(抽样看被判无措的样本对不对)。"""
import openpyxl, re, json
from collections import defaultdict

wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
recs=defaultdict(list); title={}
for r in ws.iter_rows(min_row=2,values_only=True):
    k=f"{r[0]}-{r[1]}"
    recs[k].append({"sec":float(r[4]),"w":int(r[5]),"txt":str(r[6] or "")})
    title[k]=str(r[2])

GIVEUP=["不知道","不会","不清楚","忘了","没想好","想不出","不懂","不晓得","没想到","我不"]
FILLERS=set("嗯呃啊哦额呐呢吧的了")  # 纯语气/助词
def rep_score(t):
    t=re.sub(r"[，。！？、\s]","",t)
    return sum(1 for i in range(len(t)-3) if t[i:i+2]==t[i+2:i+4])
def is_hes(txt,w):
    t=txt.strip()
    if not t: return False,""
    core=re.sub(r"[，。！？、\s]","",t)
    # 纯填充:整句只由语气词构成
    if core and all(c in "嗯呃啊哦额呐呢" for c in core): return True,"纯填充"
    # 放弃词:明确说不会/不知道
    if any(g in t for g in GIVEUP) and w<=15: return True,"放弃词"
    # 重复结巴:重复度异常高
    if w>=6 and rep_score(t)>=max(4,w*0.25): return True,"重复结巴"
    # 去掉开头语气词后,剩余内容为空或只剩语气词=无措;若剩下是实词(紧张/害怕等)=有效答案,不算无措
    stripped=re.sub(r"^[嗯呃啊哦额呢吧，。！？\s]+","",t)
    stripped_core=re.sub(r"[，。！？、\s]","",stripped)
    if len(stripped_core)==0: return True,"纯填充"  # 去掉语气词啥也不剩
    if len(stripped_core)<=1 and stripped_core in FILLERS: return True,"短填充"
    return False,""

# 自检:抽样看被判"短填充"的,是不是误伤了有效短答
print("=== 自检:被判'短填充'的样本(看是否误伤 紧张/害怕 这类有效答案) ===")
cnt=0
for k,rs in recs.items():
    for r in rs:
        h,kind=is_hes(r["txt"],r["w"])
        if kind=="短填充" and cnt<20:
            print(f"  {r['w']}字: 「{r['txt'].strip()}」")
            cnt+=1
print()

rows=[]
for k,rs in recs.items():
    n=len(rs)
    hes=sum(1 for r in rs if is_hes(r["txt"],r["w"])[0])
    slow=[r for r in rs if r["sec"]>5]
    slow_long=[r for r in slow if r["w"]>=15]
    rows.append({"k":k,"title":title[k],"n":n,
        "hes_rate":round(hes/n*100,1),
        "slow_share":round(len(slow)/n*100,1),
        "cond_long":round(len(slow_long)/len(slow)*100,1) if slow else 0})
json.dump(rows,open("/Users/kanyun/voice-ui-demos/quadrant.json","w"),ensure_ascii=False)
print("已存 quadrant.json,共",len(rows),"题")
