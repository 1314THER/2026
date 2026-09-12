# 代码/figlib 里第三方文件的来源与许可

本目录**不是**本次竞赛原创代码，而是两套开源材料的模块，按各自许可随包分发。
保留它们是为了让插图生成的"视觉语言"和"出图自检闭环"两件事都能在离线、
无 Codex 运行时的环境里跑起来。

---

## 1. `figstyle.py`、`nature-standard.md`、`visualization-rules.md`

* 来源：GitHub 开源仓库 **`Escap1ng/mathmodel-kit`** 中
  `skills/mathmodel-figure/` 下的 `code/style/plot_style.py` 与两份规范文档。
  按该文件头部注明的许可为 **Apache License 2.0**。
* 用途：插图的视觉语言——身份色/方向色/层级色三职能配色、细轴线无上右边框、
  小字、仅单方向浅灰虚线网格。
* 本地适配（仅两处，已在 `figstyle.py` 顶部写明）：
  1. `pick_cjk_font` 的候选字体表加入 macOS 常见中文字体（Songti SC / Heiti SC 等）；
  2. 顶部补上来源声明。

## 2. `export_figure.py`、`visual_qa.py`

* 来源：开源 skill 仓库 **`scipilot-figure-skill`**（作者 Haojae，**MIT License**）。
  完整许可文本见同目录 `LICENSE-scipilot-figure-skill.txt`。
* 用途：出图自检闭环——渲染中分辨率预览、程序自检（缺字乱码 / 文字越界 /
  刻度标签重叠）、导出矢量 PDF + 300 dpi PNG + 灰度预览。
* 本地适配：文件内容未改；调用方 `代码/make_figures.py` 直接
  `sys.path.insert(0, 代码/figlib)` 导入，不再依赖本机 skill 目录。

## 3. 其余文件

`代码/make_figures.py`、`代码/prepare_figure_data.py`、求解器与全部结果文件
均为本次参赛工作，不属于上述第三方。
