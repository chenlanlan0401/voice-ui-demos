#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成思考提示分层最终方案:每题等级+建议文案。"""
import json
rows=json.load(open("/Users/kanyun/voice-ui-demos/hint_data.json"))

# 分层
def tier(s):
    if s>40: return ("强提示","strong")
    if s>=20: return ("轻提示","light")
    return ("不提示","none")

# 建议文案(按题目性质拟,二年级口吻,温暖不催促)
copy_map={
    "466170-1":"这道题要你替斑比写一段心里话,先在脑子里想清楚想说什么,不着急,想好了慢慢讲给我听。",
    "466172-1":"悄悄话要好好组织一下呀,你可以先想想最想说什么,不用急着开口,准备好了再说。",
    "466974-1":"这里要回忆好几件事,别慌,慢慢在书里找一找、想一想,想全了再告诉我。",
    "398696-2":"这个问题可以多想想,有好几种办法呢,不着急,想到了就说。",
    "466973-1":"回忆一下刚才读的内容,慢慢想,想清楚了再回答。",
    "398695-1":"先体会一下斑比的心情,不用急,想好了用一句完整的话说出来。",
    "398696-1":"这个问题要动动脑筋,想想他俩各自在顾虑什么,慢慢来。",
    "466170-2":"可以发挥想象,想想斑比下次会怎么做,不着急,想到了就讲。",
}

tier_order={"强提示":0,"轻提示":1,"不提示":2}
out=[]
for r in rows:
    tname,tkey=tier(r["slow_share"])
    out.append({**r,"tier":tname,"tkey":tkey,
        "copy":copy_map.get(r["k"],"") if tname!="不提示" else ""})

out.sort(key=lambda x:(tier_order[x["tier"]], -x["slow_share"]))

print("思考提示分层方案")
print("="*90)
cur=None
for r in out:
    if r["tier"]!=cur:
        cur=r["tier"]
        cnt=sum(1 for x in out if x["tier"]==cur)
        print(f"\n【{cur}】({cnt}道)")
    line=f"  {r['k']} 慢答{r['slow_share']}%({r['n_slow']}人) {r['title'][:18]}"
    print(line)
    if r["copy"]:
        print(f"      💬 {r['copy']}")

json.dump(out,open("/Users/kanyun/voice-ui-demos/hint_final.json","w"),ensure_ascii=False)
n_s=sum(1 for x in out if x["tier"]=="强提示")
n_l=sum(1 for x in out if x["tier"]=="轻提示")
n_n=sum(1 for x in out if x["tier"]=="不提示")
print(f"\n汇总: 强提示{n_s}道 / 轻提示{n_l}道 / 不提示{n_n}道")
