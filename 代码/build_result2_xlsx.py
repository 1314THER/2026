#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 result2.xlsx（流式写入）。

结果矩阵为 2 张工作表 x 约 20.7 万行 x 22 列，合计约 910 万个单元格。
把整张表放进内存再保存（openpyxl 普通模式）会吃掉几个 GB，因此这里用
openpyxl 的 ``write_only`` 流式模式 —— 它逐行落盘，峰值内存与行数无关。

注意 write_only 模式的一个坑：``ws.column_dimensions``、``ws.freeze_panes``、
``ws.sheet_view.showGridLines`` 在该模式下**不会写进文件**（openpyxl 只在
普通模式下序列化它们）。所以字体、小数位、表头底色必须**逐个单元格**套在
``WriteOnlyCell`` 上（样式对象复用同一份，样式表会去重，文件体积不受影响），
而列宽/冻结窗格/网格线在保存后由 ``patch_sheet_view`` 直接补进工作表 XML。

输入: 输出/result2.bin、输出/result_meta.json
输出: 输出/result2.xlsx

运行:
    PY=./.venv/bin/python
    $PY 代码/build_result2_xlsx.py
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from xlsx_style import (  # noqa: E402
    BORDER_COLOR, COL_A_WIDTH, COL_WIDTH, FONT_NAME, FONT_SIZE, HEADER_FILL,
    HEADER_LABEL, NUMFMT,
)

PROJECT = HERE.parent
OUT = PROJECT / "输出"

_BODY_FONT = Font(name=FONT_NAME, size=FONT_SIZE)
_HEAD_FONT = Font(name=FONT_NAME, size=FONT_SIZE, bold=True)
_HEAD_FILL = PatternFill("solid", fgColor=HEADER_FILL)
_THIN = Side(style="thin", color=BORDER_COLOR)
_HEAD_BORDER = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)


def cell(ws, value, header=False, first_col=False):
    c = WriteOnlyCell(ws, value=value)
    c.number_format = NUMFMT
    c.font = _HEAD_FONT if header else _BODY_FONT
    if header:
        c.fill = _HEAD_FILL
        c.border = _HEAD_BORDER
        if first_col:
            c.alignment = Alignment(horizontal="left")
    return c


def write_sheet(ws, times, grid, positions):
    """A 列时间，其后各径向位置；NaN（无定义的位置）留空。"""
    n_pos = len(positions)
    ws.append([cell(ws, HEADER_LABEL, header=True, first_col=True)]
              + [cell(ws, p, header=True) for p in positions])
    for i, t in enumerate(times):
        base = i * n_pos
        vals = np.round(grid[base:base + n_pos], 4)
        row = [cell(ws, float(t))]
        row.extend(cell(ws, None if not np.isfinite(v) else float(v))
                   for v in vals)
        ws.append(row)


def patch_sheet_view(path, n_cols):
    """把 write_only 模式丢掉的列宽、冻结窗格、隐藏网格线补进 xlsx。

    做法是改 zip 里的 ``xl/worksheets/sheetN.xml``：``<cols>`` 必须插在
    ``<sheetData>`` 之前（CT_Worksheet 的元素顺序是固定的），冻结窗格写成
    ``<pane>`` 并置于 ``<sheetView>`` 的第一个子元素。改完全部 XML 都用
    ElementTree 解析一遍，确保生成的文件结构合法（否则 Excel 会报"文件损坏"）。
    """
    cols = ('<cols><col min="1" max="1" width="%g" customWidth="1"/>'
            '<col min="2" max="%d" width="%g" customWidth="1"/></cols>'
            % (COL_A_WIDTH, n_cols, COL_WIDTH))
    pane = ('<pane xSplit="1" ySplit="1" topLeftCell="B2" '
            'activePane="bottomRight" state="frozen"/>')
    tmp = path.with_name(path.stem + ".tmp" + path.suffix)
    patched = 0
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(
            tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", item.filename):
                s = data.decode("utf-8")
                if "<cols>" not in s:
                    s = s.replace("<sheetView ",
                                  '<sheetView showGridLines="0" ', 1)
                    s = re.sub(r"(<sheetView [^>]*>)", r"\1" + pane, s, count=1)
                    s = re.sub(r"(<sheetData>)", cols + r"\1", s, count=1)
                    ET.fromstring(s)                 # 结构不合法就抛出来
                    data = s.encode("utf-8")
                    patched += 1
            zout.writestr(item, data)
    shutil.move(str(tmp), str(path))
    return patched


def main():
    t0 = time.time()
    meta = json.loads((OUT / "result_meta.json").read_text(encoding="utf-8"))
    positions = meta["positions_cm"]
    n = meta["n2"]
    n_pos = len(positions)

    arr = np.fromfile(OUT / "result2.bin", dtype="<f8")
    times = arr[:n]
    temp = arr[n:n + n * n_pos]
    conc = arr[n + n * n_pos:n + 2 * n * n_pos]

    wb = Workbook(write_only=True)
    for name, grid in (("温度", temp), ("水分浓度", conc)):
        ws = wb.create_sheet(name)
        write_sheet(ws, times, grid, positions)

    target = OUT / "result2.xlsx"
    wb.save(target)
    patched = patch_sheet_view(target, n_pos + 1)
    print("已生成: %s  (%d 行 x %d 列 x 2 表，%d 张工作表补写视图，用时 %.0f s)"
          % (target, n, n_pos + 1, patched, time.time() - t0))


if __name__ == "__main__":
    main()
