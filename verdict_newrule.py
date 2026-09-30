#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新规则(用户认可2026-09-30):慢答为核心硬门槛,长答只决定A/B子类,不能单独推该等。
1. 无措≥6% → 卡壳型(该等+提示)
2. 慢答过门槛 → 该等; 长答≥40%=A类, <40%=B类
3. 慢答没过门槛 → 不用(学生不需要时间,不管长答多高)
4. 沉默≥6% 或 意图与数据矛盾 → 叠加"留意/回查"标记
边缘:慢答在[门槛-2, 门槛)之间 → 标注edge,判不用但提示可复核。
lesson4的15题保持其定稿判定(先行试点已确认),不套新规则。
"""
import json

rows=json.load(open('all114.json'))
for r in rows:
    if r['src']=='lesson4':
        r.setdefault('edge',False); r.setdefault('note','')
        continue  # lesson4定稿不动
    over5,thr,long_all,hes,silent=r['over5'],r['thr'],r['long_all'],r['hes'],(r['silent'] or 0)
    gap=thr-over5  # 正=没过门槛
    edge = (0 < gap <= 2)  # 门槛边缘
    notes=[]
    if silent>=6: notes.append('沉默%.0f%%偏高·可回查'%silent)
    if edge: notes.append('慢答%.1f近门槛%.1f·边缘'%(over5,thr))
    r['edge']=edge

    if hes>=6:
        r['big']='卡壳型'; r['ab']=''; r['verdict']='🟡卡壳型(该等+提示)'
    elif over5>=thr:
        r['big']='该等'; r['ab']='A' if long_all>=40 else 'B'
        r['verdict']='🟢该等(%s类)'%r['ab']
    else:
        r['big']='不用'; r['ab']=''
        r['verdict']='⚪不用(慢答未过门槛)'
    if notes: r['verdict']+=' ['+' / '.join(notes)+']'
    r['note']='；'.join(notes)

json.dump(rows,open('all114.json','w'),ensure_ascii=False,indent=1)
from collections import Counter
c=Counter(r['big'] for r in rows); tot=len(rows)
print('=== 新规则下114题分布 ===')
for k in ['该等','卡壳型','留意','白等','不用']:
    if c.get(k): print('  %s: %d (%d%%)'%(k,c[k],c[k]*100//tot))
A=[r for r in rows if r['ab']=='A']; B=[r for r in rows if r['ab']=='B']
print('该等: A类%d(给缓冲) B类%d(配支架)'%(len(A),len(B)))
edge=[r for r in rows if r.get('edge')]
print()
print('=== 门槛边缘题(慢答在门槛-2以内,判不用但可复核)%d道 ==='%len(edge))
for r in sorted(edge,key=lambda x:x['qid']):
    print('  %s %s年 慢答%s(门槛%s) 长答%s 沉默%s | %s'%(r['qid'],r['g'],r['over5'],r['thr'],r['long_all'],r['silent'],r['fullq'][:30]))
