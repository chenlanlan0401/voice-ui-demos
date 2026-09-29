#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版:
 老师判断 = "组织答案耗时"多因素评分(不再用提取/生成二分)
 学生数据 = 慢答(时机) + 全体长答率(篇幅) + 无措(质量) 三信号合看
 两者交叉。标黄短答题(是怎样的鹿/用一个词)按用户意见=不给。
"""
import json
sig={x['k']:x for x in json.load(open("/Users/kanyun/voice-ui-demos/signals_v2.json"))}

# 老师判断:组织答案耗时评分
# 四因素,每个题人工标(0/1/2),总分越高=组织答案越费时
# f1 自己构建(书里无现成答案):0=书里有 1=部分 2=全靠自己
# f2 组织成篇/讲理由:0=一个词/是非 1=一句话 2=一段/要理由
# f3 推理/设想/代入:0=直接反应 1=单步 2=多步/设想未来
# f4 情感卷入:0=无 1=有
teacher_score={
'466170-1':(2,2,2,1,'代入斑比写回信:全自创+成篇+设想+共情'),
'466172-1':(2,2,1,1,'说悄悄话:自创+成篇+共情'),
'466170-2':(2,1,2,0,'设想下次怎么做:自创+设想未来'),
'398695-2':(2,1,2,1,'代入你会怎么做:自创+设想+共情'),
'398696-2':(2,1,2,0,'想办法:自创+设想'),
'398696-1':(1,2,2,0,'为什么没开口:讲理由+多步推断'),
'466171-1':(2,1,2,0,'如果不开口会怎样:设想+推演后果'),
'466169-1':(1,1,2,0,'为什么竖耳朵:因果推断'),
'466168-2':(1,0,1,0,'是怎样的鹿:要判断但答案短'),
'466169-2':(1,0,1,0,'用一个词形容:要提炼但答案就一个词'),
'398695-1':(0,0,1,1,'什么心情:书里有暗示+浅共情,答案短'),
'466974-1':(0,2,0,0,'做了哪些事:提取但要串联多件事成篇'),
'466973-1':(0,1,0,0,'出现后做了什么:提取单项'),
'466168-1':(0,0,0,0,'什么反应:提取单项直接找'),
'466975-1':(0,0,0,0,'还害怕吗:是非提取'),
}
def teacher_verdict(k):
    f1,f2,f3,f4,desc=teacher_score[k]
    s=f1+f2+f3+f4
    # 分档:>=5 强该给; 3-4 该给; 2 中间; <=1 不该给
    if s>=5: tj="该等"
    elif s>=3: tj="该等"
    elif s==2: tj="中间"
    else: tj="不该等"
    return tj,s,desc

# 学生数据三信号画像
SLOW_HI=25; LONG_HI=50; HES_HI=8
def profile(x):
    s=x['slow_share']>=SLOW_HI; l=x['long_all']>=LONG_HI; h=x['hes_rate']>=HES_HI
    if h: return "卡壳无措(要时间+提示)","hint"
    if s and l: return "从容深度作答","deep"
    if s and not l: return "需要时间·答偏短","short"
    if not s and l: return "少数人从容憋长答","fewdeep"
    return "秒答顺畅","fast"
def data_support(pk): return pk!="fast"

rows=[]
for k,x in sig.items():
    tj,ts,desc=teacher_verdict(k)
    pf,pk=profile(x)
    ds=data_support(pk)
    # 交叉
    if tj=="该等" and ds: v="🟢 该等"
    elif tj=="该等" and not ds: v="🟡 该等(题型定·数据弱)"
    elif tj=="中间" and ds: v="🟢 该等(中间+数据支持)"
    elif tj=="中间" and not ds: v="⚪ 不用(中间+数据弱)"
    elif tj=="不该等" and pk=="hint": v="🟠 回查题目"
    elif tj=="不该等" and ds: v="🟠 留意"
    else: v="⚪ 不用"
    # 用户指定:标黄短答题不给
    if k in ("466168-2","466169-2"): v="⚪ 不给(用户定:短答题)"
    rows.append({'k':k,'title':x['title'],'ts':ts,'tj':tj,'desc':desc,
        'slow':x['slow_share'],'long':x['long_all'],'hes':x['hes_rate'],
        'pf':pf,'v':v})

vorder=['🟢 该等','🟢 该等(中间+数据支持)','🟡 该等(题型定·数据弱)',
        '🟠 回查题目','🟠 留意','⚪ 不用(中间+数据弱)','⚪ 不给(用户定:短答题)','⚪ 不用']
rows.sort(key=lambda r:(vorder.index(r['v']),-r['ts'],-r['slow']))
print(f"{'结论':<24}{'耗时分':>4} {'题目':<15}{'慢答':>5}{'长答':>5}{'无措':>5}  画像")
print("-"*100)
for r in rows:
    print(f"{r['v']:<24}{r['ts']:>4}  {r['title'][:13]:<15}{r['slow']:>5}{r['long']:>5}{r['hes']:>5}  {r['pf']}")
from collections import Counter
c=Counter(r['v'] for r in rows)
print("\n汇总:", dict(c))
json.dump(rows,open("/Users/kanyun/voice-ui-demos/final_v3.json","w"),ensure_ascii=False)
