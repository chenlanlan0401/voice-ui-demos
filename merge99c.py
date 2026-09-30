#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并99题首轮四信号(粒度已修正:每chatid首轮)+旧报告慢答over5+意图。"""
import csv, json

# 首轮三信号(题级)
sig={}
for f in ['sig99b_batch1.csv','sig99b_batch2.csv']:
    for r in csv.DictReader(open(f, encoding='utf-8-sig')):
        sig[r['questionid']]={'n':int(r['n']),'silent':float(r['silent']),
                              'long_all':float(r['long_all']),'hes':float(r['hes'])}

# 意图原文
intent={}
for r in csv.DictReader(open('intent99.csv', encoding='utf-8-sig')):
    intent[r['id']]={'content':r['content'],'intent':r.get('intent','')}

# 旧报告小问级(scatter, 已剔二年级)
rest=json.load(open('rest_no_g2.json'))
rows=[]
for r in rest:
    qid=r['qid']; s=sig.get(qid,{}); info=intent.get(qid,{})
    rows.append({'g':r['g'],'qid':qid,'N':r['N'],
        'over5':r['over5'],'thr':r['thr'],'stuck':r['stuck'],'oldcls':r['cls'],
        'n':s.get('n'),'silent':s.get('silent'),'long_all':s.get('long_all'),'hes':s.get('hes'),
        'content':info.get('content',''),'intent':info.get('intent','')})

miss=[r['qid'] for r in rows if r['silent'] is None]
print(f'99小问,四信号缺失qid:{len(set(miss))}',set(miss) if miss else '(无)')
json.dump(rows,open('sig99_final.json','w'),ensure_ascii=False,indent=1)
import statistics as st
print('n(人数): 中位%d min%d max%d'%(st.median(r['n'] for r in rows),min(r['n'] for r in rows),max(r['n'] for r in rows)))
for k in ['over5','silent','long_all','hes']:
    v=[r[k] for r in rows]
    print(f'{k:>9}: 中位{st.median(v):.1f} min{min(v):.1f} max{max(v):.1f}')
