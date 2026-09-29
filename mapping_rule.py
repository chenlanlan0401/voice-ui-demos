#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
映射规则:输入 原始题型 + 题干,输出 该不该给思考时间。
核心:题干关键词优先(比原始题型准),原始题型兜底。
先在lesson4的15题上自测准确率。
"""
import openpyxl

# 我的人工最终判断(金标准)
GOLD={
'466170-1':'该等','466172-1':'该等','466170-2':'该等','398695-2':'该等','398696-2':'该等',
'398696-1':'该等','466171-1':'该等','466169-1':'该等','466168-2':'该等','466169-2':'该等',
'398695-1':'中间','466974-1':'该等','466973-1':'不该等','466168-1':'不该等','466975-1':'不该等',
}

def judge(qtype, title):
    """返回 (该等/中间/不该等, 命中的规则)"""
    t=title
    # ===== 规则1:生成/表达/设想类 —— 该等(最强信号) =====
    # 代入创作、说观点、设想未来
    if any(k in t for k in ["请你当","你会怎么做","可以怎么做","会怎么做","把想对","讲出来","写一"]):
        return "该等","生成/表达/设想(代入创作或设想未来)"
    if "如果" in t and any(k in t for k in ["会","怎么","可能"]):
        return "该等","假设推演(如果…会…)"
    # ===== 规则2:推断/因果类 —— 该等 =====
    if "为什么" in t:
        return "该等","因果推断(为什么)"
    # ===== 规则3:评价/概括类 —— 该等(但答案可能短) =====
    if any(k in t for k in ["你觉得","怎样的","用一个词","用什么词","形容"]):
        return "该等","评价概括(要提炼判断,答案可短)"
    # ===== 规则4:多项提取 —— 中间偏该 =====
    if any(k in t for k in ["哪些","做了哪些","有哪些"]):
        return "中间","多项提取(要串联多件事)"
    # ===== 规则5:情感体会 —— 中间 =====
    if any(k in t for k in ["心情","什么感受","什么感觉"]):
        return "中间","情感体会(浅推断)"
    # ===== 规则6:单一事实/是非提取 —— 不该等 =====
    if any(k in t for k in ["做了什么","是什么反应","还害怕吗","是不是","有没有","在哪"]):
        return "不该等","单项/是非提取(书里找得到)"
    # ===== 兜底:靠原始题型 =====
    if qtype in ["开放表达题","人物心理题","信息推断题","人物形象题"]:
        return "该等",f"兜底:原始题型={qtype}(偏生成/推断)"
    return "不该等",f"兜底:原始题型={qtype}(偏提取)"

# 自测
wb=openpyxl.load_workbook('bambi-lesson4-data.xlsx',data_only=True)
rows=[]
for r in wb['15题总览'].iter_rows(min_row=2,values_only=True):
    k=f'{r[0]}-{r[1]}'
    rows.append((k,r[2],str(r[3])))

# 金标准里"该等短"归为"该等","中间偏该"归为"该等"做二值对比时用
def norm(v): return "该等" if v.startswith("该等") else ("中间" if v=="中间" else "不该等")

print(f"{'题干':<26}{'原始题型':<8}{'规则判断':<7}{'人工金标准':<8}{'一致?':<5} 命中规则")
print("-"*100)
correct=0
for k,qt,title in rows:
    pred,rule=judge(qt,title)
    gold=norm(GOLD[k])
    ok = "✅" if pred==gold else "❌"
    if pred==gold: correct+=1
    print(f"{title[:13]:<26}{qt:<8}{pred:<7}{gold:<8}{ok:<5} {rule}")
print("-"*100)
print(f"准确率: {correct}/{len(rows)} = {correct/len(rows)*100:.0f}%")
