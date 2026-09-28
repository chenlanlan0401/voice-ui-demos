#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
造一份贴近真实的 mock 数据：一节课 15 道题，500 个学生。
每条记录：学生在某题上的「思考时间(秒)」和「回答字数」。
输出：每题的统计聚合 + 全量原始点(供箱线图/散点用)，写成 JSON 嵌进 HTML。
"""
import json, random, math

random.seed(42)
N_STUDENTS = 500
N_QUESTIONS = 15

# 给每道题预设一个「真实难度画像」，让 mock 数据有故事可讲。
# base_median: 该题思考时间中位数(秒)
# spread: 离散程度(越大越参差)
# skew_stuck: 卡壳长尾比例(有多少学生会明显发呆/卡住)
# words_per_sec: 思考质量画像——同样时间下说得多还是少
# type: 题型标签
QUESTIONS = [
    {"id":1,  "title":"课程热身：今天心情打卡", "type":"热身互动", "base":6,  "spread":3,  "stuck":0.02, "wps":2.2},
    {"id":2,  "title":"复述上节课的一个知识点",   "type":"回忆复述", "base":12, "spread":5,  "stuck":0.05, "wps":1.8},
    {"id":3,  "title":"看图说出物体名称",         "type":"事实识别", "base":8,  "spread":4,  "stuck":0.03, "wps":1.5},
    {"id":4,  "title":"朗读并纠正一句话的语病",   "type":"语言应用", "base":18, "spread":7,  "stuck":0.08, "wps":1.6},
    {"id":5,  "title":"这道应用题该怎么列式",     "type":"逻辑推理", "base":34, "spread":14, "stuck":0.18, "wps":0.9},
    {"id":6,  "title":"选出正确选项(单选)",       "type":"事实识别", "base":9,  "spread":4,  "stuck":0.04, "wps":0.6},
    {"id":7,  "title":"用自己的话解释这个概念",   "type":"开放表达", "base":28, "spread":11, "stuck":0.12, "wps":2.0},
    {"id":8,  "title":"判断对错并说明理由",       "type":"逻辑推理", "base":30, "spread":12, "stuck":0.15, "wps":1.4},
    {"id":9,  "title":"跟读一遍这个单词",         "type":"语言应用", "base":5,  "spread":2,  "stuck":0.02, "wps":1.0},
    {"id":10, "title":"这段话主要讲了什么",       "type":"阅读理解", "base":24, "spread":9,  "stuck":0.10, "wps":1.9},
    {"id":11, "title":"举一个生活中的例子",       "type":"开放表达", "base":26, "spread":13, "stuck":0.16, "wps":2.1},
    {"id":12, "title":"多步计算：先算什么再算什么","type":"逻辑推理", "base":40, "spread":16, "stuck":0.22, "wps":0.8},
    {"id":13, "title":"你同意文中的观点吗",       "type":"开放表达", "base":22, "spread":12, "stuck":0.14, "wps":2.3},
    {"id":14, "title":"填空：补全这句古诗",       "type":"回忆复述", "base":11, "spread":6,  "stuck":0.09, "wps":0.7},
    {"id":15, "title":"课堂总结：今天学到了什么", "type":"开放表达", "base":20, "spread":10, "stuck":0.11, "wps":2.0},
]

def lognormal_time(base, spread, stuck):
    """用对数正态造思考时间：右偏(少数人特别久)，符合真实反应时间分布。"""
    # 把 base 当中位数，spread 折算成 sigma
    sigma = min(0.9, spread / base + 0.25)
    mu = math.log(base)
    t = random.lognormvariate(mu, sigma)
    # 卡壳长尾：一部分学生额外叠加一段发呆时间
    if random.random() < stuck:
        t += random.uniform(base*0.8, base*2.5)
    return max(1.0, t)

def quantile(sorted_vals, q):
    if not sorted_vals: return 0
    idx = (len(sorted_vals)-1) * q
    lo = int(math.floor(idx)); hi = int(math.ceil(idx))
    if lo == hi: return sorted_vals[lo]
    return sorted_vals[lo] + (sorted_vals[hi]-sorted_vals[lo]) * (idx-lo)

records = []          # 全量原始记录
per_q_times = {q["id"]: [] for q in QUESTIONS}
per_q_words = {q["id"]: [] for q in QUESTIONS}

# 给每个学生一个「个人快慢系数」，模拟有的学生整体就是慢/快
student_factor = [random.lognormvariate(0, 0.25) for _ in range(N_STUDENTS)]

for q in QUESTIONS:
    for s in range(N_STUDENTS):
        t = lognormal_time(q["base"], q["spread"], q["stuck"]) * student_factor[s]
        t = round(t, 1)
        # 回答字数：和思考时间弱相关 + 题型 wps + 噪声；卡壳的人可能说得很少
        words = t * q["wps"] * random.uniform(0.6, 1.4)
        # 少数人思考久但说不出来(卡壳/不会)
        if random.random() < q["stuck"] and t > q["base"]*1.5:
            words *= random.uniform(0.1, 0.4)
        words = max(0, int(round(words)))
        records.append({"q": q["id"], "s": s, "t": t, "w": words})
        per_q_times[q["id"]].append(t)
        per_q_words[q["id"]].append(words)

# 聚合每题统计
summary = []
for q in QUESTIONS:
    times = sorted(per_q_times[q["id"]])
    words = sorted(per_q_words[q["id"]])
    med = quantile(times, 0.5)
    p25 = quantile(times, 0.25)
    p75 = quantile(times, 0.75)
    p10 = quantile(times, 0.10)
    p90 = quantile(times, 0.90)
    mean = sum(times)/len(times)
    med_w = quantile(words, 0.5)
    summary.append({
        "id": q["id"], "title": q["title"], "type": q["type"],
        "n": len(times),
        "median": round(med,1), "mean": round(mean,1),
        "p25": round(p25,1), "p75": round(p75,1),
        "p10": round(p10,1), "p90": round(p90,1),
        "iqr": round(p75-p25,1),
        "median_words": int(med_w),
        # 思考效率：每秒吐出的字数(中位)。低=思考久却说得少(疑似卡壳)
        "efficiency": round(med_w/med,2) if med>0 else 0,
    })

# 抽样原始点给散点图(全量 7500 点太多，每题抽 80 个)
scatter = []
for q in QUESTIONS:
    pts = [r for r in records if r["q"]==q["id"]]
    for r in random.sample(pts, min(80, len(pts))):
        scatter.append({"q": r["q"], "t": r["t"], "w": r["w"]})

# 箱线图用的五数概括已在 summary 里，另存每题的原始时间数组(降采样)供小提琴/抖动
box_samples = {}
for q in QUESTIONS:
    vals = per_q_times[q["id"]]
    box_samples[q["id"]] = [round(v,1) for v in random.sample(vals, min(120, len(vals)))]

out = {
    "meta": {"students": N_STUDENTS, "questions": N_QUESTIONS, "total_records": len(records)},
    "summary": summary,
    "scatter": scatter,
    "box_samples": box_samples,
}

with open("/Users/kanyun/voice-ui-demos/thinking_data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)

# 打印一个文字版结论速览，方便核对
print("=== 各题思考时间(秒)排序 ===")
for row in sorted(summary, key=lambda x: x["median"], reverse=True):
    print(f"Q{row['id']:>2} {row['title'][:14]:<14} 中位{row['median']:>5}s  "
          f"IQR{row['iqr']:>5}s  中位字数{row['median_words']:>3}  效率{row['efficiency']}")
print(f"\n总记录数: {len(records)}")
