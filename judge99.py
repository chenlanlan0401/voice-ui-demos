#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按lesson4同逻辑给99题判定:老师意图×四信号。
意图动词规则(照lesson4):解释/推断/设想/表达/还原/评价=该等; 提取=不该等; 概括/比较/梳理=中间。
四信号阈值照lesson4:慢答用各年级门槛thr; 长答≥45%算高; 无措≥8%算高危; 沉默≥6%偏高。"""
import csv, json

rows=json.load(open('sig99.json'))

# 意图文本
intent={}
for r in csv.DictReader(open('intent99.csv', encoding='utf-8-sig')):
    intent[r['id']]={'content':r['content'],'intent':r.get('intent','')}

# 意图→老师判断(动词匹配)
DENG=['解释','推断','推测','设想','想象','表达','还原','评价','体会','感受','为什么','说说','谈谈','如果你']
BUDENG=['提取','找出','看屏幕','读内容','朗读','复述']
ZHONG=['概括','比较','梳理','归纳','总结']
def teacher(txt):
    t=(txt or '')
    for k in BUDENG:
        if k in t: return '不该等'
    for k in ZHONG:
        if k in t: return '中间'
    for k in DENG:
        if k in t: return '该等'
    return '中间'  # 默认中间,待人工看

for r in rows:
    info=intent.get(r['qid'],{})
    r['content']=info.get('content','')
    r['intent']=info.get('intent','')
    # 老师判断:优先看intent文本,没有则看题目content
    src=info.get('intent','') or info.get('content','')
    r['teacher']=teacher(src)

json.dump(rows,open('judge99.json','w'),ensure_ascii=False,indent=1)
from collections import Counter
print('老师意图判断分布:',dict(Counter(r['teacher'] for r in rows)))
print('已存 judge99.json,含意图+四信号')
print()
print('样例(前8):')
for r in rows[:8]:
    print('  {}-{} g{} [{}] 慢{} 长{} 无措{} 沉默{}  意图:{}'.format(
        r['qid'],r['N'],r['g'],r['teacher'],r['over5'],r['long_all'],r['hes'],r['silent'],(r['intent'] or r['content'])[:20]))
