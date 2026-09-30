#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从旧报告lat_curves直方图给99题算over6/over7(慢答6秒/7秒),看衰减+是否改判。
档位确认:>5秒=p[5:], >6秒=p[6:], >7秒=p[7:] (与over5吻合,|diff|中位0.1)。
lat_curves与scatter同序一一对应。"""
import json
d=json.load(open('mic_timing_118.json'))
sc=d['scatter']; lc=d['verify_thr']['lat_curves']
# scatter[i] <-> lc[i], 建 (qid,N)->over6/over7
o67={}
for i in range(118):
    r=sc[i]; p=lc[i]['p']
    o67[(r['qid'],str(r['N']))]={'over6':round(sum(p[6:]),1),'over7':round(sum(p[7:]),1)}

rows=json.load(open('verdict99_A.json'))
for r in rows:
    k=(r['qid'],str(r['N']))
    e=o67.get(k,{})
    r['over6']=e.get('over6'); r['over7']=e.get('over7')

miss=[r['qid'] for r in rows if r['over6'] is None]
print('缺over6/7的:',len(miss),set(miss) if miss else '(无)')
json.dump(rows,open('verdict99_A.json','w'),ensure_ascii=False,indent=1)

import statistics as st
print('慢答口径衰减(99题中位): 5秒%.1f → 6秒%.1f → 7秒%.1f'%(
    st.median(r['over5'] for r in rows),st.median(r['over6'] for r in rows),st.median(r['over7'] for r in rows)))

# 关键:用7秒口径重判,看"该等"里哪些题7秒塌了(慢答被延迟灌水)
print()
print('=== 该等题里,慢答5→7秒衰减最狠的(可能是延迟灌水,7秒后不够该等) ===')
deng=[r for r in rows if '该等' in r['verdict'] and '卡壳' not in r['verdict']]
for r in sorted(deng,key=lambda x:-(x['over5']-x['over7']))[:12]:
    drop=r['over5']-r['over7']
    print('  %s-%s g%s 慢答 %.1f→%.1f→%.1f (掉%.1f) 长%.1f 意图%s %s'%(
        r['qid'],r['N'],r['g'],r['over5'],r['over6'],r['over7'],drop,r['long_all'],r['teacher'],r['verdict']))
