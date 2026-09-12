#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从论文 .tex 里抽出表 1-表 6，导出成 输出/基准值-论文表1到表6.json。

为什么需要
----------
`verify_paper_numbers.py` 会拿重算出的数据与论文表 1-表 6 的每一个数字比对。
本包不包含论文（`论文/` 目录不在这里），所以打包时先把这 6 张表导成一份 JSON
当作基准值；比对脚本在没有 .tex 时读它，有 .tex 时仍直接读正文，两条路等价。

运行（只有手上有论文源文件时才需要重跑）:
    PY=./.venv/bin/python
    $PY 代码/export_baseline_tables.py --tex /path/to/论文全文.tex
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT / "输出" / "基准值-论文表1到表6.json"

LABELS = ["tab:p1-T", "tab:p1-C", "tab:p2-T", "tab:p2-C", "tab:p3", "tab:p4"]


def tex_table(src: str, label: str):
    """从 .tex 正文里取出指定 label 的表体，返回 [(行标签, [单元格...]), ...]。"""
    for t in re.findall(r"\\begin\{table\}(.*?)\\end\{table\}", src, re.S):
        if "\\label{%s}" % label not in t:
            continue
        body = t.split("\\midrule", 1)[1].split("\\bottomrule", 1)[0]
        rows = []
        for line in body.split("\\\\"):
            line = re.sub(r"\\cmidrule[^\s]*(\{[^}]*\})*", "", line)
            line = line.replace("\\midrule", "").strip()
            if not line or line.startswith("\\multicolumn"):
                continue
            cells = [c.strip().replace("\\,", "").replace("$", "")
                     for c in line.split("&")]
            if len(cells) >= 2 and cells[0]:
                rows.append((cells[0], cells[1:]))
        return rows
    raise KeyError(label)


def main() -> None:
    ap = argparse.ArgumentParser(description="导出论文表 1-表 6 的基准值")
    ap.add_argument("--tex", default=str(PROJECT / "论文" / "论文全文.tex"))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    src = Path(args.tex).read_text(encoding="utf-8")
    out = {lab: tex_table(src, lab) for lab in LABELS}
    Path(args.out).write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("已导出: %s" % args.out)
    for k, v in out.items():
        print("  %-10s %d 行" % (k, len(v)))


if __name__ == "__main__":
    main()
