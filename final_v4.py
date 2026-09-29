#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""定稿v4:出题人配置(问题意图+dialogType) + 学生三信号 融合。"""
import json
sig={x['k']:x for x in json.load(open("signals_v2.json"))}

# 出题人配置(察察取到)
config={
'466170-1':('board_interaction','还原老鹿王两层心理','两个空都要答到'),
'466172-1':('board_interaction','邀请自愿表达一句想说的话','开放表达'),
'398696-1':('voice_interaction','解释双方为何没开口','任一方有效原因'),
'398696-2':('voice_interaction','想一种帮助表达的做法','设想做法'),
'466171-1':('voice_interaction','推断持续沉默的后果','任一合理后果'),
'466169-1':('voice_interaction','解释绕路听动静的原因','任一因果方向'),
'398695-1':('voice_interaction','推断斑比真实心情','答到任一近义心情即可'),
'398695-2':('voice_interaction','设想自己会怎么做','开放设想'),
'466168-1':('voice_interaction','提取斑比的反应','答到任一项即可'),
'466168-2':('voice_interaction','评价老鹿王是只怎样的鹿','一个判断词'),
'466169-2':('voice_interaction','用一个词概括','一个词'),
'466170-2':('voice_interaction','设想下次见面怎么做','开放设想'),
'466973-1':('voice_interaction','提取关键行动','说出任一核心意思即可'),
'466974-1':('voice_interaction','提取并概括三组行动','三组行动'),
'466975-1':('voice_interaction','比较前后变化并用原文说明','任一组有效变化+说明'),
}
# 意图动词→老师判断
def teacher_by_intent(intent, expect):
    # 提取类=不该等; 但"概括/比较/说明"要串联=中间; 解释/推断/还原/表达/设想=该等
    if '设想' in intent or '推断' in intent or '解释' in intent or '还原' in intent or '表达' in intent or '评价' in intent:
        return '该等'
    if '概括' in intent or '比较' in intent:
        return '中间'  # 提取但要加工
    if '提取' in intent:
        return '不该等'
    return '中间'

SLOW_HI=25; LONG_HI=50; HES_HI=8
def profile(x):
    s=x['slow_share']>=SLOW_HI; l=x['long_all']>=LONG_HI; h=x['hes_rate']>=HES_HI
    if h: return "卡壳无措","hint"
    if s and l: return "从容深度作答","deep"
    if s and not l: return "需要时间·答偏短","short"
    if not s and l: return "少数人从容憋长答","fewdeep"
    return "秒答顺畅","fast"

rows=[]
for k,x in sig.items():
    dt,intent,expect=config[k]
    tj=teacher_by_intent(intent,expect)
    pf,pk=profile(x)
    ds = pk!="fast"
    # 交叉
    if tj=="该等" and ds: v="🟢 该等"
    elif tj=="该等" and not ds: v="🟡 该等(意图定·数据弱)"
    elif tj=="中间" and ds: v="🟢 该等(中间+数据支持)"
    elif tj=="中间" and not ds: v="🟡 偏该等(意图偏提取+数据弱)"
    elif tj=="不该等" and pk=="hint": v="🟠 回查题目"
    elif tj=="不该等" and ds: v="🟠 留意"
    else: v="⚪ 不用"
    # 用户指定短答题不给
    if k in ("466168-2","466169-2"): v="⚪ 不给(用户定:短答题)"
    rows.append({'k':k,'title':x['title'],'dt':dt,'intent':intent,'tj':tj,
        'slow':x['slow_share'],'long':x['long_all'],'hes':x['hes_rate'],'pf':pf,'v':v})

vorder=['🟢 该等','🟢 该等(中间+数据支持)','🟡 该等(意图定·数据弱)','🟡 偏该等(意图偏提取+数据弱)',
        '🟠 回查题目','🟠 留意','⚪ 不给(用户定:短答题)','⚪ 不用']
rows.sort(key=lambda r:(vorder.index(r['v']),-r['slow']))
print(f"{'结论':<22}{'题目':<15}{'交互':<6}{'出题人意图':<22}{'慢':>4}{'长':>4}{'措':>4} 画像")
print("-"*112)
for r in rows:
    dt='板书' if r['dt']=='board_interaction' else '语音'
    print(f"{r['v']:<22}{r['title'][:13]:<15}{dt:<6}{r['intent'][:20]:<22}{r['slow']:>4}{r['long']:>4}{r['hes']:>4} {r['pf']}")
from collections import Counter
c=Counter(r['v'] for r in rows)
print("\n汇总:")
for k in vorder:
    if c[k]: print(f"  {k}: {c[k]}道")
json.dump(rows,open("final_v4.json","w"),ensure_ascii=False)
