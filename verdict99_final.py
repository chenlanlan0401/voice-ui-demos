#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终判定:意图×行为共同判断,★行为否决原则(用户2026-09-30定):
意图想深 但 学生行为明确秒答短答(慢答远低门槛 且 长答很低)→ 判不用,行为优先。
另修正2道意图:334695/893326 提取但需整理→改判该等。
"""
import json,csv
rows=json.load(open('verdict99_A.json'))
intent={}
for r in csv.DictReader(open('intent99.csv',encoding='utf-8-sig')):
    intent[r['id']]={'content':r['content']}
for r in rows: r['content']=intent.get(r['qid'],{}).get('content','')

# 修正意图(用户复核):334695/893326 提取但需整理组织→该等
for r in rows:
    if r['qid'] in ('334695','893326'): r['teacher']='该等'

def verdict(r):
    over5,over7,thr,long_all,hes,silent=r['over5'],r['over7'],r['thr'],r['long_all'],r['hes'],r['silent']
    t=r['teacher']; gap=thr-over5
    # ★行为否决:学生明确秒答短答(慢答明显低于门槛 且 长答很低)→ 不用,不管意图
    behavior_no = (over5 < thr-3) and (long_all < 15)
    if hes>=6: return '🟡卡壳型(该等+提示)'
    if behavior_no: return '⚪不用(行为否决:秒答短答)'
    if t=='该等':
        if over5>=thr or long_all>=45: return '🟢该等(意图+数据)'
        return '🟢该等(意图强,数据尚可)'
    if t=='不该等':
        if over5>=thr and long_all>=45: return '🔵留意(意图提取但数据强该等)'
        return '⚪不用(提取题)'
    if over5>=thr and long_all>=45: return '🟢该等(中间+数据)'
    if over5>=thr and long_all<45: return '🟠白等(慢但答不长)'
    if silent>=6: return '🔵留意(沉默偏高)'
    return '⚪不用'

for r in rows: r['verdict']=verdict(r)
json.dump(rows,open('verdict99_final.json','w'),ensure_ascii=False,indent=1)

from collections import Counter
def big(v):
    if '该等' in v and '卡壳' not in v: return '该等'
    if '卡壳' in v: return '卡壳型'
    if '白等' in v: return '白等'
    if '留意' in v: return '留意'
    return '不用'
print('=== 最终判定大类(行为否决原则后) ===')
tot=len(rows)
for k,v in Counter(big(r['verdict']) for r in rows).most_common():
    print(f'  {k}: {v} ({v*100//tot}%)')
print()
print('=== 明细档 ===')
for k,v in Counter(r['verdict'] for r in rows).most_common(): print(f'  {k}: {v}')
# 真正站得住的翻案题
flip=[r for r in rows if r['oldcls'] in ('OK','B') and big(r['verdict']) in ('该等','卡壳型')]
print(f'\n真翻案题(旧不用/白等→新该等/卡壳,行为否决后): {len(flip)}道')
