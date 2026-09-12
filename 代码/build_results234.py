#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 result3.xlsx / result4.xlsx（result2 见 build_result2_xlsx.py）。

输入: 输出/result3.bin、result4.bin、result_meta.json
      （由 代码/prepare_outputs.py 生成）
输出: 输出/result3.xlsx、输出/result4.xlsx

格式遵循题面附件 3 的模板:
    - A 列为时间 (单位: s)，第 1 行为到药材中心的距离 (单位: cm)
    - result3、result4 只含水分浓度；result4 末列为 "药材表面"
    - 超出当前半径的位置留空（问题四收缩后 R < 2 cm）
    - 所有数值保留四位小数

result2.xlsx 有 970 万个单元格，用 openpyxl 的流式模式单独生成；
本文件里的两张表只有几千行，直接整表写即可。

运行:
    PY=./.venv/bin/python
    $PY 代码/build_results234.py          # result3 与 result4
    $PY 代码/build_results234.py 3        # 只生成 result3
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from openpyxl import Workbook

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from xlsx_style import write_sheet  # noqa: E402

PROJECT = HERE.parent
OUT = PROJECT / "输出"


def read_f64(path):
    return np.fromfile(path, dtype="<f8")


def build3(meta, positions):
    n = meta["n3"]
    n_pos = len(positions)
    arr = read_f64(OUT / "result3.bin")
    times = arr[:n]
    conc = arr[n:n + n * n_pos]
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    write_sheet(ws, times, conc, positions)
    target = OUT / "result3.xlsx"
    wb.save(target)
    print("已生成: %s  (%d 行 x %d 列)" % (target, n, n_pos + 1))


def build4(meta, positions):
    n = meta["n4"]
    n_pos = len(positions)
    arr = read_f64(OUT / "result4.bin")
    times = arr[:n]
    conc = arr[n:n + n * n_pos]
    surf = arr[n + n * n_pos:n + n * n_pos + n]
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    write_sheet(ws, times, conc, positions, extra_name="药材表面", extra=surf)
    target = OUT / "result4.xlsx"
    wb.save(target)
    print("已生成: %s  (%d 行 x %d 列 + 药材表面)"
          % (target, n, n_pos + 1))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "34"
    meta = json.loads((OUT / "result_meta.json").read_text(encoding="utf-8"))
    positions = meta["positions_cm"]
    if which in ("all", "34", "3", "4"):
        if which in ("all", "34", "3"):
            build3(meta, positions)
        if which in ("all", "34", "4"):
            build4(meta, positions)
    elif which == "2":
        raise SystemExit("result2 请运行 代码/build_result2_xlsx.py")
    else:
        raise SystemExit("用法: build_results234.py [3|4|34]")


if __name__ == "__main__":
    main()
