#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""环境自检：解释器、四个依赖、中文字体。

为什么需要它
------------
本包刻意不依赖任何"竞赛之外"的运行时（原版的 xlsx 生成依赖 Node 与
@oai/artifact-tool，现已改为纯 Python + openpyxl），所以在一台干净的机器上
只需要"一个 Python 解释器 + 四个 pip 包"。

唯一容易踩的坑是**中文字体**：插图里有中文标签，若系统一个覆盖简体中文的字体
都没有，matplotlib 会把它们渲染成方框（而且只在 stderr 告警，不抛异常）。
本脚本把这件事提前查出来。

运行:
    ./.venv/bin/python 代码/check_env.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "figlib"))

MIN_PY = (3, 9)


def main() -> int:
    ok = True
    print("解释器      : %s" % sys.executable)
    print("Python 版本 : %s" % sys.version.split()[0])
    if sys.version_info < MIN_PY:
        print("  ✗ 需要 Python %d.%d 及以上" % MIN_PY)
        ok = False

    print("\n依赖:")
    for name in ("numpy", "openpyxl", "matplotlib", "seaborn"):
        try:
            mod = __import__(name)
            print("  ✓ %-11s %s" % (name, getattr(mod, "__version__", "?")))
        except ImportError as exc:
            print("  ✗ %-11s 缺失（%s）" % (name, exc))
            ok = False

    if not ok:
        print("\n依赖不全：先执行 ./setup.sh（或 pip install -r requirements.txt）")
        return 1

    # ---- 中文字体 ----
    from matplotlib import font_manager

    installed = {f.name for f in font_manager.fontManager.ttflist}
    print("\n中文字体（插图里的中文标签靠它）:")
    cands = ("Arial Unicode MS", "Hiragino Sans GB", "PingFang SC",
             "Heiti SC", "Songti SC", "STHeiti", "STSong", "SimHei",
             "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC",
             "WenQuanYi Zen Hei", "Noto Sans SC")
    hit = [c for c in cands if c in installed]
    if hit:
        for c in hit:
            print("  ✓ %s%s" % (c, "（首选，Latin+CJK+数学符号全覆盖）"
                                if c == "Arial Unicode MS" else ""))
        print("  字体栈会自动优先使用已安装的那一个（见 代码/figlib/figstyle.py）")
    else:
        print("  ✗ 没有找到任何中文字体，插图里的中文会变成方框")
        print("    解决办法：装一个中文字体后重跑，例如")
        print("      macOS : 安装 Arial Unicode MS（Office 自带）或 Songti SC")
        print("      Linux : apt install fonts-noto-cjk")
        print("      Win   : 自带 SimHei / Microsoft YaHei")
        ok = False

    from matplotlib import rcParams  # noqa: F401
    print("\n数据目录:")
    for p in ("附件", "输出", "代码"):
        print("  %s %s" % ("✓" if (HERE.parent / p).exists() else "✗", p))

    print("\n环境自检%s" % ("通过。" if ok else "未通过，请先解决上面标 ✗ 的问题。"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
