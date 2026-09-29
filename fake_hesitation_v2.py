#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
假性无措 v2:收紧口径——有实义的短答一律保留,只认真正的逃避/卡壳信号。
无措只判 3 类(去掉了误伤有效短答的"短填充"):
  A 放弃词:明确说 不知道/不会/忘了/想不出… (w<=15,避免长答里顺带提到)
  B 纯填充:整句只由 嗯/呃/啊/哦/额 等语气词构成
  C 重复结巴:同一短串大量连续重复(喂喂喂喂 / 呀呀呀呀)
'伤心''勇敢''警惕''面包'这类有实义的两字词 = 有效答案,不算无措。
再按开口秒数切,看真·假性无措规模。秒数含1-2秒链路延迟。
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

GIVEUP=["不知道","不会","不清楚","忘了","没想好","想不出","不懂","没有了","不晓得","不记得","没想到","想不起"]
def rep_score(t):
    t=re.sub(r"[，。！？、\s]","",t); reps=0
    for i in range(len(t)-3):
        if t[i:i+2]==t[i+2:i+4]: reps+=1
    return reps
def is_hesitation(txt,w):
    t=txt.strip()
    if not t: return False,""
    core=re.sub(r"[，。！？、\s~～]","",t)
    if not core: return False,""
    # B 纯填充:整句只有语气词
    if all(c in "嗯呃啊哦额呐哈唉" for c in core): return True,"纯填充"
    # A 放弃词:明确逃避,且不是长答里顺带
    if any(g in t for g in GIVEUP) and w<=15: return True,"放弃词"
    # C 重复结巴:重复度异常高
    if len(core)>=6 and rep_score(t)>=max(4,w*0.25): return True,"重复结巴"
    return False,""

def bucket(sec):
    if sec<=2: return "≤2秒(基本没想)"
    if sec<=3: return "2-3秒(几乎秒答)"
    if sec<=5: return "3-5秒(想了一下)"
    return ">5秒(想过才放弃)"

buckets={"≤2秒(基本没想)":0,"2-3秒(几乎秒答)":0,"3-5秒(想了一下)":0,">5秒(想过才放弃)":0}
all_hes=[]; per_q=[]; kinds_g=defaultdict(int)
for k,rs in recs.items():
    n=len(rs); hes_list=[]
    for r in rs:
        h,kind=is_hesitation(r["txt"],r["w"])
        if h:
            item={"k":k,"sec":r["sec"],"w":r["w"],"txt":r["txt"],"kind":kind,"bk":bucket(r["sec"])}
            hes_list.append(item); all_hes.append(item)
            buckets[item["bk"]]+=1; kinds_g[kind]+=1
    if not hes_list:
        per_q.append({"k":k,"title":title[k],"n":n,"hes_n":0,"hes_rate":0.0,
            "fast_n":0,"fake_ratio":0.0,"fast_in_all":0.0,"slow_hes_n":0}); continue
    fast=[h for h in hes_list if h["sec"]<=3]
    slow_hes=[h for h in hes_list if h["sec"]>5]
    per_q.append({
        "k":k,"title":title[k],"n":n,
        "hes_n":len(hes_list),"hes_rate":round(len(hes_list)/n*100,1),
        "fast_n":len(fast),
        "fake_ratio":round(len(fast)/len(hes_list)*100,1),
        "fast_in_all":round(len(fast)/n*100,1),
        "slow_hes_n":len(slow_hes)})

tot=len(all_hes)
print(f"收紧后 全课无措样本总数: {tot}  (v1旧口径是782)")
print("无措类型分布:", dict(kinds_g))
print("="*70)
print("【无措样本 按开口秒数分桶】(秒数含1-2秒链路延迟)")
for b,c in buckets.items():
    print(f"  {b:<18} {c:>4} 条  ({c/tot*100:.1f}%)")
fake=buckets["≤2秒(基本没想)"]+buckets["2-3秒(几乎秒答)"]
print(f"\n  →→ ≤3秒'假性无措'共 {fake} 条,占全部无措 {fake/tot*100:.1f}%")

print("\n"+"="*70)
print("【按题:假性无措占比】fake_ratio=秒答无措/该题无措数  fast_in_all=秒答无措占全体%")
pq=[q for q in per_q if q["hes_n"]>=8]
pq.sort(key=lambda x:-x["fast_in_all"])
print(f"{'题号':<11}{'无措率%':>7}{'无措数':>6}{'秒答无措':>7}{'占全体%':>7}{'假性占比%':>9}  题目")
for q in pq:
    print(f"{q['k']:<11}{q['hes_rate']:>7}{q['hes_n']:>6}{q['fast_n']:>7}{q['fast_in_all']:>7}{q['fake_ratio']:>9}  {q['title'][:15]}")

print("\n"+"="*70)
print("【≤3秒 无措样本 抽样】(收紧后应基本都是真逃避)")
fa=sorted([h for h in all_hes if h["sec"]<=3],key=lambda x:x["sec"])
for h in fa[:30]:
    print(f"  [{h['k']}] {h['sec']}s/{h['w']}字 [{h['kind']}]: {h['txt'][:34]}")

json.dump({"buckets":buckets,"tot_hes":tot,"kinds":dict(kinds_g),"fake_total":fake,
    "fake_share_of_hes":round(fake/tot*100,1),"per_q":per_q},
    open("/Users/kanyun/voice-ui-demos/fake_hesitation.json","w"),ensure_ascii=False,indent=1)
