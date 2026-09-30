#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并99小问的四信号:慢答over5(旧报告scatter,小问级) + 沉默/无措/长答(对话表,题级)。"""
import csv, json

# 对话表四信号(题级 questionid)
sig={}
for f in ['sig_batch1.csv','sig_batch2.csv']:
    for r in csv.DictReader(open(f, encoding='utf-8-sig')):
        sig[r['questionid']]={'turns':int(r['turns']),'silent':float(r['silent']),
                              'hes':float(r['hes']),'long_all':float(r['long_all'])}

# 旧报告小问级(scatter),已剔二年级
rest=json.load(open('rest_no_g2.json'))

rows=[]
for r in rest:
    qid=r['qid']; s=sig.get(qid,{})
    rows.append({'g':r['g'],'qid':qid,'N':r['N'],
        'over5':r['over5'],'thr':r['thr'],'stuck':r['stuck'],'oldcls':r['cls'],
        'silent':s.get('silent'),'hes':s.get('hes'),'long_all':s.get('long_all'),'turns':s.get('turns')})

# 检查有无缺失
miss=[r['qid'] for r in rows if r['silent'] is None]
print(f'99小问,缺四信号的:{len(set(miss))}个qid', set(miss) if miss else '')
json.dump(rows,open('sig99.json','w'),ensure_ascii=False,indent=1)
print('已存 sig99.json')
print()
# 概览:四信号分布
import statistics as st
for k in ['over5','silent','hes','long_all','stuck']:
    vals=[r[k] for r in rows if r[k] is not None]
    print(f'{k:>9}: 中位{st.median(vals):.1f}  min{min(vals):.1f}  max{max(vals):.1f}')
