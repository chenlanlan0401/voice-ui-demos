#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
假性无措深挖:把所有"无措"样本按开口秒数切开。
核心假设(用户最感兴趣的机会点):
  很多"不知道/呃/嗯"其实是 1-3 秒的秒答,是被"立刻收音"的压力逼出来的逃避,
  不是真的不会。如果给一点喘息+心理许可,这些人本可以答出来。
判定口径完全复用 hesitation_score.py。
开口秒数含 1-2 秒链路延迟,所以真实思考时间要在显示值上再减 1-2 秒。
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
def rep_score(t):
    t=re.sub(r"[，。！？、\s]","",t); reps=0
    for i in range(len(t)-3):
        if t[i:i+2]==t[i+2:i+4]: reps+=1
    return reps
def is_hesitation(txt,w):
    t=txt.strip()
    if not t: return False,""
    core=re.sub(r"[，。！？、\s]","",t)
    if core and all(c in "嗯呃啊哦额呐" for c in core): return True,"纯填充"
    if any(g in t for g in GIVEUP) and w<=15: return True,"放弃词"
    if w>=6 and rep_score(t)>=max(4,w*0.25): return True,"重复结巴"
    if w<=6:
        stripped=re.sub(r"^[嗯呃啊哦额，。\s]+","",t)
        if len(re.sub(r"[，。！？、\s]","",stripped))<=2: return True,"短填充"
    return False,""

# 全局:所有无措样本按秒数分桶
buckets={"≤2秒(基本没想)":0,"2-3秒(几乎秒答)":0,"3-5秒(想了一下)":0,">5秒(想过才放弃)":0}
def bucket(sec):
    if sec<=2: return "≤2秒(基本没想)"
    if sec<=3: return "2-3秒(几乎秒答)"
    if sec<=5: return "3-5秒(想了一下)"
    return ">5秒(想过才放弃)"

all_hes=[]
per_q=[]
for k,rs in recs.items():
    n=len(rs); hes_list=[]
    for r in rs:
        h,kind=is_hesitation(r["txt"],r["w"])
        if h:
            item={"k":k,"sec":r["sec"],"w":r["w"],"txt":r["txt"],"kind":kind,"bk":bucket(r["sec"])}
            hes_list.append(item); all_hes.append(item); buckets[item["bk"]]+=1
    if not hes_list: continue
    fast=[h for h in hes_list if h["sec"]<=3]   # 秒答型无措=假性无措候选
    slow_hes=[h for h in hes_list if h["sec"]>5]
    per_q.append({
        "k":k,"title":title[k],"n":n,
        "hes_n":len(hes_list),"hes_rate":round(len(hes_list)/n*100,1),
        "fast_n":len(fast),                                  # ≤3秒 的无措数
        "fake_ratio":round(len(fast)/len(hes_list)*100,1),   # 假性占无措的比例
        "fast_in_all":round(len(fast)/n*100,1),              # 秒答无措占全体比例
        "slow_hes_n":len(slow_hes),                          # 真·想过才放弃
    })

tot_hes=len(all_hes)
print(f"全课无措样本总数: {tot_hes}")
print("="*70)
print("【无措样本 按开口秒数分桶】(秒数含1-2秒链路延迟)")
for b,c in buckets.items():
    print(f"  {b:<18} {c:>4} 条  ({c/tot_hes*100:.1f}%)")
fake=buckets["≤2秒(基本没想)"]+buckets["2-3秒(几乎秒答)"]
print(f"\n  →→ ≤3秒的'假性无措'共 {fake} 条,占全部无措 {fake/tot_hes*100:.1f}%")

print("\n"+"="*70)
print("【按题:假性无措占比】(fake_ratio=秒答无措/该题无措总数)")
per_q.sort(key=lambda x:-x["fake_ratio"])
print(f"{'题号':<11}{'无措率%':>7}{'秒答无措':>7}{'假性占比%':>9}  题目")
for q in per_q:
    print(f"{q['k']:<11}{q['hes_rate']:>7}{q['fast_n']:>7}{q['fake_ratio']:>9}  {q['title'][:16]}")

# 看看这些秒答"不知道"长什么样
print("\n"+"="*70)
print("【≤3秒 无措样本 抽样】(验证:是不是真的想都没想就逃)")
fast_all=[h for h in all_hes if h["sec"]<=3]
fast_all.sort(key=lambda x:x["sec"])
for h in fast_all[:25]:
    print(f"  [{h['k']}] {h['sec']}s/{h['w']}字 [{h['kind']}]: {h['txt'][:30]}")

json.dump({"buckets":buckets,"tot_hes":tot_hes,"fake_total":fake,
    "fake_share_of_hes":round(fake/tot_hes*100,1),"per_q":per_q},
    open("/Users/kanyun/voice-ui-demos/fake_hesitation.json","w"),ensure_ascii=False,indent=1)
