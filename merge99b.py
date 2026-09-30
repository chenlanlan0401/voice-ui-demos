#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把补齐口径的无措hes2合并进sig99,替换旧的偏低hes。"""
import csv, json

hes2={}
for f in ['hes_batch1.csv','hes_batch2.csv']:
    for r in csv.DictReader(open(f, encoding='utf-8-sig')):
        hes2[r['questionid']]=float(r['hes2'])

rows=json.load(open('sig99.json'))
for r in rows:
    r['hes_old']=r['hes']
    r['hes']=hes2.get(r['qid'])
json.dump(rows,open('sig99.json','w'),ensure_ascii=False,indent=1)

import statistics as st
old=[r['hes_old'] for r in rows]
new=[r['hes'] for r in rows]
print(f'无措率口径补齐前后对比(99小问):')
print(f'  旧(仅放弃词): 中位{st.median(old):.1f} max{max(old):.1f}')
print(f'  新(+纯填充+结巴): 中位{st.median(new):.1f} max{max(new):.1f}')
print()
print('无措最高的10道(新口径):')
for r in sorted(rows,key=lambda x:-x['hes'])[:10]:
    print('  {}-{} g{}  无措{}  慢答{}  沉默{}  长答{}  旧cls={}'.format(
        r['qid'],r['N'],r['g'],r['hes'],r['over5'],r['silent'],r['long_all'],r['oldcls']))
