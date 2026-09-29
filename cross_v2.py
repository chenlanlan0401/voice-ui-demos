#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
15题:老师判断 × 学生数据(慢答+长答+无措三信号合看)。
学生数据画像:
 - 慢答=开口时机  长答=字数篇幅  无措=内容质量
 三者合成一个"学生画像"标签,再和老师判断交叉。
"""
import json
q=json.load(open("/Users/kanyun/voice-ui-demos/quadrant.json"))
d={x['k']:x for x in q}

teacher={
'466170-1':('该等','创作表达'),'466172-1':('该等','创作表达'),
'466170-2':('该等','设想'),'398695-2':('该等','设想·共情'),
'398696-2':('该等','设想'),'398696-1':('该等','推断·多步'),
'466171-1':('该等','推断·设想'),'466169-1':('该等','推断·因果'),
'466168-2':('该等','评价概括'),'466169-2':('该等','评价概括'),
'398695-1':('中间','情感体会'),'466974-1':('中间','多项提取'),
'466973-1':('不该等','单项提取'),'466168-1':('不该等','单项提取'),
'466975-1':('不该等','是非提取'),
}

# 三信号阈值
SLOW_HI=25; LONG_HI=55; HES_HI=8
def profile(x):
    slow=x['slow_share']; longr=x['cond_long']; hes=x['hes_rate']
    s_hi=slow>=SLOW_HI; l_hi=longr>=LONG_HI; h_hi=hes>=HES_HI
    # 画像判定
    if h_hi:
        return "卡壳无措(要时间+要提示)","hint"
    if s_hi and l_hi:
        return "从容深度作答(最该给)","deep"
    if s_hi and not l_hi:
        return "需要时间·答偏短","short"
    if not s_hi and l_hi:
        return "少数人从容憋长答","fewdeep"
    return "秒答顺畅(基本不用)","fast"

def data_lean(pkey):
    # 数据倾向:是否支持该等
    return pkey in ("deep","hint","short","fewdeep")  # 只有fast=明显不支持

order_p={"hint":0,"deep":1,"short":2,"fewdeep":3,"fast":4}
rows=[]
for k,x in d.items():
    tj,tt=teacher[k]
    pf,pk=profile(x)
    ds=data_lean(pk)
    # 交叉
    if tj=="该等" and ds: v="🟢 该等"
    elif tj=="该等" and not ds: v="🟡 该等(题型定·数据弱)"
    elif tj=="中间" and ds: v="🟢 该等(中间+数据支持)"
    elif tj=="中间" and not ds: v="⚪ 不用(中间+数据不支持)"
    elif tj=="不该等" and pk=="hint": v="🟠 回查题目(简单却大量无措)"
    elif tj=="不该等" and ds: v="🟠 留意(简单却数据偏高)"
    else: v="⚪ 不用"
    rows.append({'k':k,'title':x['title'],'tt':tt,'tj':tj,
        'slow':x['slow_share'],'long':x['cond_long'],'hes':x['hes_rate'],
        'pf':pf,'pk':pk,'v':v})

vorder=['🟢 该等','🟢 该等(中间+数据支持)','🟡 该等(题型定·数据弱)',
        '🟠 回查题目(简单却大量无措)','🟠 留意(简单却数据偏高)',
        '⚪ 不用(中间+数据不支持)','⚪ 不用']
rows.sort(key=lambda r:(vorder.index(r['v']),-r['slow']))
print(f"{'结论':<26}{'题目':<15}{'认知类型':<10}{'慢答':>5}{'长答':>5}{'无措':>5}  学生画像")
print("-"*104)
for r in rows:
    print(f"{r['v']:<26}{r['title'][:13]:<15}{r['tt']:<10}{r['slow']:>5}{r['long']:>5}{r['hes']:>5}  {r['pf']}")
