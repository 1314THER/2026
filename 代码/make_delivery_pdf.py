#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把编译好的论文 PDF 缩成符合竞赛格式的交付版（A4 + 不小于 2.5 cm 页边距）。

为什么要这一步
--------------
竞赛《论文格式规范》第一条要求"上下左右各留出至少 2.5 厘米的页边距"。
正文排版本身是按 2.2 cm 左右页边距做的（\geometry{left=2.2cm,right=2.2cm,
top=2.6cm,bottom=2.4cm}），直接打印会不满足这一条；而把 geometry 改成
2.5 cm 会让每行变短、全文重排、页数增加（正文已用到第 30 页的上限）。

这里采取不改排版的**整体缩放**：把原 PDF 的每一页按同一比例缩小后居中放到
A4 上。缩放是等比的，所以**分页完全不变**（正文仍为 29 页），没有任何内容被
裁掉。缩放比例由"缩放后四边页边距都不小于 2.5 cm"反解得到：

    缩放后页边距 = s·m + P(1-s)/2 ≥ 2.5 cm      （m 为原页边距，P 为页宽或页高）

脚本会先把原 PDF 每页的**实际墨迹包围盒**量一遍（文字 + 矢量图 + 位图，含页眉
页脚），取四边各自的最小值再解 s，因此不会出现"缩完还有某页贴边"的情况。

依赖：PyMuPDF（`pip install pymupdf`），只用于重新拼版，不改变文字与矢量图。

运行:
    python3 代码/make_delivery_pdf.py 论文/论文全文.pdf 论文/论文全文_交付版.pdf
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF

CM = 72.0 / 2.54                       # 1 cm = 28.3465 pt
A4_W, A4_H = 21.0 * CM, 29.7 * CM


def ink_box(page):
    """页面内容的实际包围盒（文字 + 矢量绘图 + 位图），用于核验页边距。"""
    boxes = []
    for b in page.get_text("blocks"):
        boxes.append(fitz.Rect(b[:4]))
    for d in page.get_drawings():
        boxes.append(fitz.Rect(d["rect"]))
    for img in page.get_image_info():
        boxes.append(fitz.Rect(img["bbox"]))
    boxes = [b for b in boxes if b.width > 0 and b.height > 0]
    if not boxes:
        return None
    box = boxes[0]
    for b in boxes[1:]:
        box |= b
    return box


def margins_cm(page, box=None):
    box = box or ink_box(page)
    if box is None:
        return None
    r = page.rect
    return (box.x0 / CM, (r.width - box.x1) / CM,
            box.y0 / CM, (r.height - box.y1) / CM)


def worst_margins(doc):
    """整份 PDF 四边各自的最小页边距 / cm。"""
    worst = [1e9] * 4
    for page in doc:
        m = margins_cm(page)
        if m:
            worst = [min(a, b) for a, b in zip(worst, m)]
    return worst


def solve_scale(worst, w_cm, h_cm, target_cm=2.5):
    """解出"四边都不小于 target_cm"所需的最大缩放比例（≤1）。

    两端都用 cm：worst 是实测页边距，w_cm/h_cm 是页面宽高。
    """
    cands = []
    for m, p_cm in ((worst[0], w_cm), (worst[1], w_cm),
                    (worst[2], h_cm), (worst[3], h_cm)):
        a = m - p_cm / 2.0
        b = target_cm - p_cm / 2.0
        if a < 0:                     # 该边的页边距可以靠缩小拉开
            cands.append(b / a)
    return min(min(cands), 1.0) if cands else 1.0


def main() -> int:
    ap = argparse.ArgumentParser(description="生成满足 2.5 cm 页边距的交付版 PDF")
    ap.add_argument("src", help="编译出来的原 PDF")
    ap.add_argument("dst", help="交付版 PDF 的输出路径")
    ap.add_argument("--scale", type=float, default=None,
                    help="缩放比例（默认按左右页边距恰好 2.5 cm 反解）")
    args = ap.parse_args()

    src_path, dst_path = Path(args.src), Path(args.dst)
    src = fitz.open(src_path)
    if src.page_count == 0:
        raise SystemExit("源 PDF 没有页面: %s" % src_path)

    # 量原版四边的最小页边距，再解出满足 2.5 cm 的比例；也可用 --scale 手动指定
    worst_src = worst_margins(src)
    scale = args.scale if args.scale else solve_scale(
        worst_src, A4_W / CM, A4_H / CM, 2.5)
    print("原版最小页边距: 左 %.2f / 右 %.2f / 上 %.2f / 下 %.2f cm"
          % tuple(worst_src))

    out = fitz.open()
    for page in src:
        w, h = page.rect.width, page.rect.height
        nw, nh = w * scale, h * scale
        new_page = out.new_page(width=w, height=h)      # 输出仍是 A4
        rect = fitz.Rect((w - nw) / 2, (h - nh) / 2,
                         (w + nw) / 2, (h + nh) / 2)
        new_page.show_pdf_page(rect, src, page.number)  # 矢量、文字原样搬过去

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst_path, garbage=4, deflate=True)

    # ---- 自检：页数、页面尺寸、四边页边距 ----
    chk = fitz.open(dst_path)
    worst = worst_margins(chk)
    print("缩放比例 : %.5f（内容整体缩小 %.2f%%）" % (scale, 100 * (1 - scale)))
    print("页数     : %d（与原版一致，分页未变）" % chk.page_count)
    print("页面尺寸 : %.2f x %.2f cm" % (chk[0].rect.width / CM,
                                         chk[0].rect.height / CM))
    print("最小页边距: 左 %.2f / 右 %.2f / 上 %.2f / 下 %.2f cm（要求 ≥2.5）"
          % tuple(worst))
    print("文件大小 : %.2f MB" % (dst_path.stat().st_size / 1024 / 1024))
    ok = min(worst) >= 2.5 - 0.02
    print("页边距自检: %s" % ("通过" if ok else "★不通过"))
    print("已输出: %s" % dst_path)

    if not ok:
        print("提示: 若某页有图形越出新页边距，可加 --scale 0.95 再跑一次")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
