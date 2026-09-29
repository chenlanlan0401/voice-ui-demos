#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每道题:题干全文 + 四项打分明细 + 表现数据 + 分档原话。分批输出。"""
import openpyxl, re, json, sys
from collections import defaultdict

wb=openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-rowlevel.xlsx",data_only=True)
ws=wb["作答明细"]
recs=defaultdict(list); title={}
for r in ws.iter_rows(min_row=2,values_only=True):
    k=f"{r[0]}-{r[1]}"
    recs[k].append({"sec":float(r[4]),"w":int(r[5]),"txt":str(r[6] or "")})
    title[k]=str(r[2])

sig={x['k']:x for x in json.load(open("signals_v2.json"))}
FV={x['k']:x['v'] for x in json.load(open("final_v3.json"))}

# 四项打分 (F1自己构建, F2组织成篇, F3推理设想, F4情感卷入) + 每项理由
SCORE={
'466170-1':((2,2,2,1),("书里无·全自创","要写一整段","设想+代入","代入斑比情感")),
'466172-1':((2,2,1,1),("书里无·全自创","要说一段心里话","单步表达","共情")),
'398695-2':((2,1,2,1),("书里无·全自创","一句话即可","设想未来+代入","代入自己")),
'398696-2':((2,1,2,0),("书里无·想办法","一句话即可","设想未来","无")),
'398696-1':((1,2,2,0),("部分需推理","要讲理由成段","多步推断心理","无")),
'466170-2':((2,1,2,0),("书里无·自创","一句话即可","设想未来","无")),
'466171-1':((2,1,2,0),("书里无·假设","一句话即可","设想后果","无")),
'466169-1':((1,1,2,0),("部分需推理","一句话即可","因果推断","无")),
'466974-1':((0,2,0,0),("书里有","要串联多件事成段","直接回忆","无")),
'398695-1':((0,0,1,1),("书里有暗示","答案短(情绪词)","浅推断","共情")),
'466168-2':((1,0,1,0),("需判断","答案短(一个判断)","单步评价","无")),
'466169-2':((1,0,1,0),("需提炼","答案短(一个词)","单步概括","无")),
'466973-1':((0,1,0,0),("书里有","一句话","直接找","无")),
'466168-1':((0,0,0,0),("书里有","短","直接找","无")),
'466975-1':((0,0,0,0),("书里有","是非","直接判","无")),
}
def verdict(s):
    if s>=5: return "该等(强)"
    if s>=3: return "该等"
    if s==2: return "中间"
    return "不该等"

GIVEUP=["不知道","不会","不清楚","忘了","没想好","想不出","不懂","不晓得","没想到","我不"]
def rep_score(t):
    t=re.sub(r"[，。！？、\s]","",t); return sum(1 for i in range(len(t)-3) if t[i:i+2]==t[i+2:i+4])
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

# 顺序:按耗时分降序
keys=sorted(recs.keys(), key=lambda k:-sum(SCORE[k][0]))
batch=int(sys.argv[1]) if len(sys.argv)>1 else 0
sel=keys[batch*5:batch*5+5]

for k in sel:
    rs=recs[k]; x=sig[k]
    (f1,f2,f3,f4),(r1,r2,r3,r4)=SCORE[k]
    s=f1+f2+f3+f4
    print("="*82)
    print(f"{k}  题干:「{title[k]}」")
    print(f"  ── 老师判断(看题干)──  总分{s} → {verdict(s)}")
    print(f"     F1自己构建 {f1}分 ({r1})")
    print(f"     F2组织成篇 {f2}分 ({r2})")
    print(f"     F3推理设想 {f3}分 ({r3})")
    print(f"     F4情感卷入 {f4}分 ({r4})")
    print(f"  ── 学生数据 ──  慢答{x['slow_share']}% | 全体长答{x['long_all']}% | 无措{x['hes_rate']}%")
    fl=[r for r in rs if r['sec']<=3 and r['w']>=15]
    sl=[r for r in rs if r['sec']>5 and r['w']>=15]
    ss=[r for r in rs if r['sec']>5 and r['w']<15 and not is_hes(r['txt'],r['w'])]
    hs=[r for r in rs if is_hes(r['txt'],r['w'])]
    def pk(l,n=3,bl=False):
        l=[r for r in l if r['txt'].strip()]
        if bl: l=sorted(l,key=lambda r:-r['w'])
        return l[:n]
    print("  ── 原话样本 ──")
    for lab,lst,bl in [("慢答·长",sl,True),("慢答·短(有效)",ss,False),("无措",hs,False)]:
        pp=pk(lst,3,bl)
        if pp:
            print(f"     [{lab}]")
            for r in pp: print(f"        {r['sec']}s/{r['w']}字: {r['txt'][:40]}")
    print(f"  ══ 最终结论:{FV[k]} ══")
