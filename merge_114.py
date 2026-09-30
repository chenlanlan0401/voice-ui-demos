#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B方案:15(lesson4)+99 合并成114题整体,统一字段,出统一结论。"""
import json
from collections import Counter

# lesson4沉默率(questionid级,HANDOFF记录)
L4_SILENT={"466973":6.9,"466172":6.8,"466974":5.6,"466169":5.4,"466171":5.2,
"466168":5.1,"466170":4.8,"398696":4.8,"398695":3.8,"466975":3.6}
# lesson4门槛(二年级)
L4_THR=24.3

# lesson4 15题
l4=json.load(open('final_v4.json'))
rows=[]
for r in l4:
    qid=r['k'].split('-')[0]
    # 判定归一
    v=r['v']
    if '该等' in v: big='该等'
    elif '留意' in v: big='留意'
    elif '不给' in v or '不用' in v: big='不用'
    else: big='不用'
    rows.append({'src':'lesson4','g':'2','qid':qid,'N':r['k'].split('-')[1],
        'fullq':r['title'],'teacher':r['tj'],
        'over5':r['slow'],'over6':None,'over7':None,'thr':L4_THR,
        'long_all':r['long'],'hes':r['hes'],'silent':L4_SILENT.get(qid),
        'big':big,'verdict':v})

# 99题
g99=json.load(open('report_full_data.json'))
def big99(v):
    if '该等' in v and '卡壳' not in v: return '该等'
    if '卡壳' in v: return '卡壳型'
    if '白等' in v: return '白等'
    if '留意' in v: return '留意'
    return '不用'
for r in g99:
    rows.append({'src':'99','g':r['g'],'qid':r['qid'],'N':str(r['N']),
        'fullq':r['fullq'],'teacher':r['teacher'],
        'over5':r['over5'],'over6':r['over6'],'over7':r['over7'],'thr':r['thr'],
        'long_all':r['long_all'],'hes':r['hes'],'silent':r['silent'],
        'big':big99(r['verdict']),'verdict':r['verdict']})

# AB子类(该等题)
for r in rows:
    if r['big']=='该等': r['ab']='A' if (r['long_all'] or 0)>=40 else 'B'
    else: r['ab']=''

json.dump(rows,open('all114.json','w'),ensure_ascii=False,indent=1)
print('合并完成,共%d题 (lesson4 %d + 99题 %d)'%(len(rows),len(l4),len(g99)))
print()
print('=== 114题整体判定分布 ===')
c=Counter(r['big'] for r in rows); tot=len(rows)
for k in ['该等','卡壳型','留意','白等','不用']:
    if c.get(k): print('  %s: %d (%d%%)'%(k,c[k],c[k]*100//tot))
print()
print('=== 该等题AB分类 ===',dict(Counter(r['ab'] for r in rows if r['ab'])))
print()
print('=== 按年级该等占比 ===')
for g in '23456':
    gr=[r for r in rows if r['g']==g]
    if not gr: continue
    d=sum(1 for r in gr if r['big']=='该等')
    print('  %s年级: 该等%d/%d (%d%%)'%(g,d,len(gr),d*100//len(gr)))
