#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15题:老师判断 × 学生数据 交叉挑题,产出最终该等清单。"""
import json
q=json.load(open("/Users/kanyun/voice-ui-demos/quadrant.json"))
d={x['k']:x for x in q}

# 老师题型判断
teacher={
'466170-1':('该等','生成·表达·共情'),'466172-1':('该等','生成·表达·共情'),
'466170-2':('该等','生成·设想'),'398695-2':('该等','生成·共情·设想'),
'398696-2':('该等','生成·设想'),'398696-1':('该等','推断·多步'),
'466171-1':('该等','推断·设想'),'466169-1':('该等','推断·因果'),
'466168-2':('该等','评价·概括(答可短)'),'466169-2':('该等','评价·概括(答必短)'),
'398695-1':('中间','浅推断·共情'),'466974-1':('中间','提取·多项'),
'466973-1':('不该等','提取·单项'),'466168-1':('不该等','提取·单项'),
'466975-1':('不该等','提取·是非'),
}

# 学生数据是否支持"该等":需要时间(慢答>=25%)或 明显无措(无措>=8%)
# 说明:慢答高=很多人需要时间;无措高=很多人不会说(也是该关注的信号)
def data_support(x):
    slow_hi = x['slow_share']>=25
    hes_hi = x['hes_rate']>=8
    if slow_hi or hes_hi: return True, f"慢答{x['slow_share']}%/无措{x['hes_rate']}%"
    return False, f"慢答{x['slow_share']}%/无措{x['hes_rate']}%"

# 四象限交叉
def cross(tj, ds):
    t_yes = tj in ("该等","中间")   # 老师认为需要关注(该等或中间都算倾向给)
    if tj=="该等" and ds: return "🟢铁定该等"
    if tj=="该等" and not ds: return "🟡存疑(题该给·数据没显现)"
    if tj=="不该等" and ds: return "🟠警示(题简单·数据却异常)"
    if tj=="不该等" and not ds: return "⚪确定不用"
    if tj=="中间" and ds: return "🟢倾向该等(中间+数据支持)"
    if tj=="中间" and not ds: return "⚪倾向不用(中间+数据不支持)"

rows=[]
for k,x in d.items():
    tj,tt=teacher[k]
    ds,dstr=data_support(x)
    verdict=cross(tj,ds)
    # 无措特别高的额外标记
    extra = " ⚠需额外给提示" if x['hes_rate']>=10 else ""
    rows.append({'k':k,'title':x['title'],'tt':tt,'tj':tj,
        'slow':x['slow_share'],'hes':x['hes_rate'],'long':x['cond_long'],
        'ds':ds,'dstr':dstr,'verdict':verdict,'extra':extra})

order=['🟢铁定该等','🟢倾向该等(中间+数据支持)','🟡存疑(题该给·数据没显现)',
       '🟠警示(题简单·数据却异常)','⚪倾向不用(中间+数据不支持)','⚪确定不用']
rows.sort(key=lambda r:(order.index(r['verdict']),-r['slow']))

for r in rows:
    print(f"{r['verdict']}|{r['title'][:16]}|{r['tt']}|慢{r['slow']}|无措{r['hes']}|长{r['long']}|{r['extra']}")

# 汇总
from collections import Counter
c=Counter(r['verdict'] for r in rows)
print("\n汇总:")
for k in order:
    if c[k]: print(f"  {k}: {c[k]}道")
