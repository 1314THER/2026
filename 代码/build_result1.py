#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由问题一的求解结果生成 result1.xlsx。

输入: 输出/result1_data.json   （由 solve_p1.py --save 自动导出）
输出: 输出/result1.xlsx

工作表格式遵循题面附件 3 的模板:
    - "温度" 与 "水分浓度" 两个工作表
    - A 列为时间 (单位: s)，第 1 行为到药材中心的距离 (单位: cm)
    - 所有数值保留四位小数

运行:
    PY=./.venv/bin/python
    $PY 代码/solve_p1.py --save 输出/result1_data.npz
    $PY 代码/build_result1.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from openpyxl import Workbook

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from xlsx_style import write_sheet  # noqa: E402

PROJECT = HERE.parent
INPUT = PROJECT / "输出" / "result1_data.json"
OUTPUT = PROJECT / "输出" / "result1.xlsx"


def main():
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    radius_cm = data["radius_cm"]
    times = data["times"]

    # 每一行必须严格对应一个时刻，避免错行
    for key in ("temperature", "moisture"):
        if len(data[key]) != len(times):
            raise SystemExit(
                "%s 行数 %d 与时间点数 %d 不一致"
                % (key, len(data[key]), len(times))
            )

    wb = Workbook()
    wb.remove(wb.active)
    for name, key in (("温度", "temperature"), ("水分浓度", "moisture")):
        ws = wb.create_sheet(name)
        rows = data[key]
        flat = [v for row in rows for v in row]
        write_sheet(ws, times, flat, radius_cm)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT)
    print("已生成: %s  (%d 行 x %d 列 x 2 表)"
          % (OUTPUT, len(times), len(radius_cm) + 1))


if __name__ == "__main__":
    main()
