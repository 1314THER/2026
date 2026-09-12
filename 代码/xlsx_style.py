#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""result1-4.xlsx 的统一样式（对齐题面附件 3 的模板）。

为什么单独抽出这个模块
----------------------
四个结果文件由三个脚本生成——result1 一个、result2 一个（表太大，必须流式
写）、result3/4 一个。它们放在同一个文件夹里交给评委，表头、字号、小数位
必须**完全一致**；把样式集中在这里，就不会出现"result2 是 Calibri 常规格式、
result3 是 Arial 四位小数"这种一眼可见的不整齐。

格式约定（与附件 3 模板一致）：
    * A1 = ``时间\\到药材中心的距离``，第 1 行为到药材中心的距离（cm）
    * A 列为时间（s），其余列为该时刻各位置的温度（°C）或水分浓度（kg/kg）
    * 全部数值四位小数显示（``0.0000``）
    * 表头浅灰底 + 细边框 + Arial 加粗；正文 Arial 10
    * 冻结首行首列、关闭网格线、A 列加宽到 23（否则长表头会被右侧挤掉）

只在标准库 + openpyxl 上实现，不依赖任何运行时的表格服务。
"""

from __future__ import annotations

import math

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HEADER_LABEL = "时间\\到药材中心的距离"
NUMFMT = "0.0000"
FONT_NAME = "Arial"
FONT_SIZE = 10
HEADER_FILL = "D9D9D9"
BORDER_COLOR = "808080"
COL_A_WIDTH = 23
COL_WIDTH = 10

_THIN = Side(style="thin", color=BORDER_COLOR)


def round4(v):
    """按模板保留四位小数；NaN（药材已收缩掉的位置）写成空白单元格。"""
    if v is None:
        return None
    v = float(v)
    if math.isnan(v) or math.isinf(v):
        return None
    return round(v, 4)


def header_style(ws, n_cols):
    """给第 1 行套表头样式。``ws`` 可以是普通 worksheet。"""
    for j in range(1, n_cols + 1):
        c = ws.cell(row=1, column=j)
        c.number_format = NUMFMT
        c.fill = PatternFill("solid", fgColor=HEADER_FILL)
        c.font = Font(name=FONT_NAME, size=FONT_SIZE, bold=True)
        c.border = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)
        if j == 1:
            c.alignment = Alignment(horizontal="left")


def body_style(ws, n_rows, n_cols):
    """给数据区（第 2 行起）套正文字体与小数位。"""
    for i in range(2, n_rows + 1):
        for j in range(1, n_cols + 1):
            c = ws.cell(row=i, column=j)
            c.number_format = NUMFMT
            c.font = Font(name=FONT_NAME, size=FONT_SIZE)


def sheet_style(ws, n_cols):
    """列宽、冻结窗格、网格线。"""
    ws.column_dimensions["A"].width = COL_A_WIDTH
    for j in range(2, n_cols + 1):
        ws.column_dimensions[get_column_letter(j)].width = COL_WIDTH
    ws.freeze_panes = "B2"
    ws.sheet_view.showGridLines = False


def write_sheet(ws, times, grid, positions, extra_name=None, extra=None,
                style_cells=True):
    """把 (时间, 网格) 写成一整张表，返回行数。

    ``grid`` 是长度 ``len(times) * len(positions)`` 的一维行主序序列
    （``result2/3/4.bin`` 的排布方式）；``extra`` 是可选的一列（问题四的
    药材表面浓度），排在最后。
    """
    n_pos = len(positions)
    headers = [HEADER_LABEL, *positions]
    if extra_name:
        headers.append(extra_name)
    n_cols = len(headers)
    ws.append(headers)
    for i, t in enumerate(times):
        base = i * n_pos
        row = [float(t)]
        row.extend(round4(v) for v in grid[base:base + n_pos])
        if extra_name:
            row.append(round4(extra[i]))
        ws.append(row)
    if style_cells:
        header_style(ws, n_cols)
        body_style(ws, len(times) + 1, n_cols)
    sheet_style(ws, n_cols)
    return n_cols
