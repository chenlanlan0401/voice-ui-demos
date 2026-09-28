#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openpyxl
wb = openpyxl.load_workbook("/Users/kanyun/voice-ui-demos/bambi-lesson4-data.xlsx", data_only=True)
print("=== 工作表 ===", wb.sheetnames)
for ws in wb.worksheets:
    print(f"\n##### Sheet: {ws.title}  维度 {ws.max_row} 行 × {ws.max_column} 列")
    # 打印表头(前2行)
    for ri, row in enumerate(ws.iter_rows(min_row=1, max_row=min(3, ws.max_row), values_only=True), 1):
        print(f"  行{ri}:", [str(c)[:22] if c is not None else "" for c in row])
    # 打印几行样本数据
    print("  --- 样本数据(第4~8行) ---")
    for ri, row in enumerate(ws.iter_rows(min_row=4, max_row=min(8, ws.max_row), values_only=True), 4):
        print(f"  行{ri}:", [str(c)[:18] if c is not None else "" for c in row])
