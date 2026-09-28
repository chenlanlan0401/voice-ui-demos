#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并三档+模糊带语义判定,生成lesson4最终清单。"""
import json
rows=json.load(open("/Users/kanyun/voice-ui-demos/final_lesson4.json"))

# 模糊带的语义判定结果(我基于任务性质+长答率+原话质量判的)
fuzzy_verdict={
    "466974-1":("该等","信息题但需复述多件事,长答是完整剧情复述,认知负荷高"),
    "466170-2":("该等","长答率83.7%全场第二,开放表达,慢的人几乎都在憋有观点的长答"),
    "398696-1":("该等","推理题需揣摩双方心理,长答在真思考"),
    "398696-2":("不该等","长答率仅52%,与398695-2近义重复,一半慢的人只是嘴慢"),
    "466169-1":("该等","长答率76.6%高,推断题需思考猎人/圈套逻辑,长答是真推断"),
    "466973-1":("不该等","长答率49%不到半,比466974更简单(单一动作),短答多敷衍"),
}

final=[]
for r in rows:
    if r["band"]=="明显该等":
        v,reason="该等","误伤率高,慢答多且长答率高,无争议"
    elif r["band"]=="明显不用":
        v,reason="不该等","误伤率低,零等待损失小"
    else:
        v,reason=fuzzy_verdict[r["key"]]
    final.append({**r,"verdict":v,"reason":reason})

# 建议等待秒数:该等的题取P75(含1-2s延迟),换算真实思考约减1.5s
print("="*95)
print("lesson4 最终判定清单")
print("="*95)
wait=[f for f in final if f["verdict"]=="该等"]
nowait=[f for f in final if f["verdict"]=="不该等"]
print(f"\n【该等 {len(wait)}道】按误伤率排:")
print(f"{'题号':<11}{'误伤%':>6}{'慢答%':>6}{'长答率%':>7}{'P75(埋点)':>9}{'真实思考≈':>9}  题目 / 判定依据")
for f in sorted(wait,key=lambda x:-x["misfire"]):
    real=round(f["p75"]-1.5,1)
    print(f"{f['key']:<11}{f['misfire']:>6}{f['slow_share']:>6}{f['cond_long']:>7}{f['p75']:>9}{real:>8}s  {f['title'][:16]}")
    print(f"{'':40}└ {f['reason']}")
print(f"\n【不该等 {len(nowait)}道】保持立即开麦:")
for f in sorted(nowait,key=lambda x:-x["misfire"]):
    print(f"{f['key']:<11}{f['misfire']:>6}{f['slow_share']:>6}{f['cond_long']:>7}  {f['title'][:18]}")

json.dump(final,open("/Users/kanyun/voice-ui-demos/final_verdict.json","w"),ensure_ascii=False)
print(f"\n汇总: 该等{len(wait)}道 / 不该等{len(nowait)}道")
print("建议等待秒数取该题慢答者开口P75(覆盖3/4慢答者),换算真实思考减~1.5s链路延迟")
