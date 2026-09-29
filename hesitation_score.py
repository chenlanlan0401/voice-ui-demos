#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给每条回答打"无措分",再按题聚合无措率,和慢答占比/长答率并排对比。
无措判定(满足任一即算无措):
 A 短填充:字数<=6 且 以填充词开头 或 整句是填充/放弃词
 B 重复结巴:重复度高(连续2字串大量重复)
 C 纯填充:整句只由 嗯/呃/啊/哦 等构成
判定要稳健:避免把"正常短答"(如"紧张""害怕")误判为无措——那些是有效答案。
"""
import openpyxl, re, json
from collections import defaultdict

wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
recs=defaultdict(list); title={}
for r in ws.iter_rows(min_row=2,values_only=True):
    k=f"{r[0]}-{r[1]}"
    recs[k].append({"sec":float(r[4]),"w":int(r[5]),"txt":str(r[6] or "")})
    title[k]=str(r[2])

GIVEUP=["不知道","不会","不清楚","忘了","没想好","想不出","不懂","没有了","不晓得"]
PURE_FILL=set("嗯呃啊哦额呐�nen ，。！？…、 ")

def rep_score(t):
    t=re.sub(r"[，。！？、\s]","",t)
    reps=0
    for i in range(len(t)-3):
        if t[i:i+2]==t[i+2:i+4]: reps+=1
    return reps

def is_hesitation(txt,w):
    t=txt.strip()
    if not t: return False,""
    core=re.sub(r"[，。！？、\s]","",t)
    # C 纯填充
    if core and all(c in "嗯呃啊哦额呐" for c in core): return True,"纯填充"
    # A 放弃词(明确说不会/不知道),不限长度
    if any(g in t for g in GIVEUP) and w<=15: return True,"放弃词"
    # B 重复结巴:字数不算太短但重复度异常高
    if w>=6 and rep_score(t)>=max(4,w*0.25): return True,"重复结巴"
    # A2 极短且以填充开头(呃/嗯 开头 且 去掉填充后剩不到3字)
    if w<=6:
        stripped=re.sub(r"^[嗯呃啊哦额，。\s]+","",t)
        if len(re.sub(r"[，。！？、\s]","",stripped))<=2: return True,"短填充"
    return False,""

rows=[]
for k,rs in recs.items():
    n=len(rs)
    hes=0; kinds=defaultdict(int)
    for r in rs:
        h,kind=is_hesitation(r["txt"],r["w"])
        if h: hes+=1; kinds[kind]+=1
    slow=[r for r in rs if r["sec"]>5]
    slow_long=[r for r in slow if r["w"]>=15]
    rows.append({"k":k,"title":title[k],"n":n,
        "hes_rate":round(hes/n*100,1),"hes_n":hes,
        "slow_share":round(len(slow)/n*100,1),
        "cond_long":round(len(slow_long)/len(slow)*100,1) if slow else 0,
        "kinds":dict(kinds)})

# 按无措率排
rows.sort(key=lambda x:-x["hes_rate"])
print("按【无措率】排序,并列出慢答占比对比")
print("="*95)
print(f"{'题号':<11}{'无措率%':>7}{'无措数':>6}{'慢答%':>7}{'长答率%':>7}  题目 / 无措类型分布")
print("-"*95)
for r in rows:
    kd=",".join(f"{k}{v}" for k,v in sorted(r["kinds"].items(),key=lambda x:-x[1]))
    print(f"{r['k']:<11}{r['hes_rate']:>7}{r['hes_n']:>6}{r['slow_share']:>7}{r['cond_long']:>7}  {r['title'][:14]} [{kd}]")

# 对比:无措率排序 vs 慢答占比排序,看是否指向不同的题
print("\n【关键对比】无措率 vs 慢答占比,谁排前面差异大?")
by_hes=sorted(rows,key=lambda x:-x["hes_rate"])
by_slow=sorted(rows,key=lambda x:-x["slow_share"])
print(f"{'排名':<4}{'无措率Top':<20}{'慢答占比Top':<20}")
for i in range(len(rows)):
    print(f"{i+1:<4}{by_hes[i]['title'][:9]+'('+str(by_hes[i]['hes_rate'])+')':<22}{by_slow[i]['title'][:9]+'('+str(by_slow[i]['slow_share'])+')':<22}")

json.dump(rows,open("/Users/kanyun/voice-ui-demos/hesitation.json","w"),ensure_ascii=False)
