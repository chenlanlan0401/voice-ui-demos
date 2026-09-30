#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B方案:纯四信号按lesson4阈值判定99题,并对照旧报告cls看结论变化。
lesson4判定逻辑复刻:
 - 慢答over5 vs 各年级门槛thr:过门槛=慢的人多
 - 长答long_all >=45% = 慢的人愿意展开(该等的正信号)
 - 无措hes >=8% = 卡壳型高危; >=5%=偏高留意
 - 沉默silent >=6% = 沉默流失偏高
判定档:
 🟢该等 = 慢答过门槛 且 长答>=45
 🟡卡壳型 = 无措>=8 (不论慢答,内容困住,该等+提示)
 🟠白等 = 慢答过门槛 但 长答<45 (慢但答不长)
 🔵留意 = 慢答近门槛(差<=3) 或 沉默>=6 或 无措5-8 (边界,需看意图)
 ⚪不用 = 慢答远低于门槛 且 其他信号都低
对照:旧报告cls(A该等/B白等/OK不用)——看新四信号是否翻案。
"""
import json
rows=json.load(open('judge99.json'))

def verdict(r):
    over5,thr,long_all,hes,silent=r['over5'],r['thr'],r['long_all'],r['hes'],r['silent']
    gap=thr-over5  # 正=没过门槛
    tags=[]
    if hes>=8: return '🟡卡壳型(该等+提示)',tags
    if over5>=thr and long_all>=45: return '🟢该等',tags
    if over5>=thr and long_all<45: return '🟠白等(慢但答不长)',tags
    # 边界/留意
    if gap<=3 or silent>=6 or hes>=5:
        if silent>=6: tags.append('沉默偏高')
        if hes>=5: tags.append('无措偏高')
        if 0<gap<=3: tags.append('慢答近门槛')
        return '🔵留意(需看意图)',tags
    return '⚪不用',tags

for r in rows:
    v,tags=verdict(r)
    r['verdict']=v; r['tags']=tags

json.dump(rows,open('verdict99.json','w'),ensure_ascii=False,indent=1)

from collections import Counter
print('=== B方案 99题判定分布 ===')
for k,v in Counter(r['verdict'] for r in rows).most_common():
    print(f'  {k}: {v}')
print()
# 对照旧报告:新判定 vs 旧cls
clsmap={'A':'旧该等','B':'旧白等','OK':'旧不用'}
print('=== 与旧报告(仅慢答+长答)对照:翻案题 ===')
print('【旧判不用/白等,新判该等或卡壳型】= 旧框架漏掉的:')
flip=[r for r in rows if r['oldcls'] in ('OK','B') and ('该等' in r['verdict'] or '卡壳' in r['verdict'])]
for r in sorted(flip,key=lambda x:-x['hes']):
    print(f"  {r['qid']}-{r['N']} g{r['g']} [{clsmap[r['oldcls']]}→{r['verdict']}] 慢{r['over5']}(门槛{r['thr']}) 长{r['long_all']} 无措{r['hes']} 沉默{r['silent']}")
print(f'\n翻案题共 {len(flip)} 道')
