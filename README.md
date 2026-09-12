# 2026 高教社杯全国大学生数学建模竞赛 A 题　药材的烘干问题
## 代码与数据包

> **本包只含代码、数据与结果文件，不含竞赛论文。**
> 论文正文（`论文全文.tex` / `.pdf`）与论文插图源码留在原项目 `论文/` 目录下，
> 未随本包分发；本包把论文用到的**全部数值结果**都从原始附件重算得到。
>
> 包内所有脚本只依赖 Python 加四个 pip 包，**不依赖任何 Codex 运行时**：
> 原版用来写 xlsx 的 Node 加 `@oai/artifact-tool` 已改写为 openpyxl 实现，
> 出图自检用到的两个外部模块已随包放进 `代码/figlib/`。

---

## 一、结果一览

| 问题 | 内容 | 结果 | 结果文件 |
| --- | --- | --- | --- |
| 一 | 预热平衡 30 min 的温度场与水分浓度场 | 中心 28 min 内含水率不变；表面 2.5500 降至 **1.5103** kg/kg；径向温差 3.21 摄氏度 | `输出/result1.xlsx` |
| 二 | 整个烘干过程的耦合模型（至 3 h） | 药材升温至约 50 摄氏度；含水率由表及里依次下降 | `输出/result2.xlsx` |
| 三 | 求烘干时长（各点 C 小于 0.15 kg/kg） | **57.42 h = 2.392 天** | `输出/result3.xlsx` |
| 四 | 计入收缩的烘干模型 | **50.31 h = 2.096 天** | `输出/result4.xlsx` |

两个求解器写的是同一套模型：圆柱坐标一维径向的耦合传热传质方程组，
节点中心有限体积离散 + 后向 Euler 时间推进 + Picard 迭代；水分方程取经典
Fick 形式，体积密度只以密度乘比热进入热方程。问题一物性为常数（两方程解耦），
问题二起物性与扩散系数随含水率、温度耦合，问题四把半径的收缩写进贴体坐标。

---

## 二、快速开始

```bash
./setup.sh              # 建 .venv，装 numpy / openpyxl / matplotlib / seaborn，并做环境自检
./reproduce.sh          # 全量复现：四个 result 文件 + 对照实验 + 派生数据 + 全部插图
./reproduce.sh --fast   # 只复现四个 result 文件与正文表格（约 8 分钟）
```

只用系统 Python 也可以，把 `./.venv/bin/python` 换成你自己的解释器路径即可
（Python 3.9 及以上；已在 3.9.6 与 3.12.14 上验证）。国内网络可用
`PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple ./setup.sh`。

**时间预算**（在一台 M 系列 Mac 上实测，总计约 64 分钟）：

| 步骤 | 用时 |
| --- | --- |
| 问题一（N=400、dt=1 s，1800 s 物理时间） | 10 s |
| 问题二/三/四（N=200、dt=5 s，61 h 物理时间） | 约 4 分钟 |
| 生成 result2.xlsx（910 万个单元格，流式写入） | 约 3 分钟 |
| 三因素对照（20 组）+ 三种口径 + 灵敏度 + 收缩判据 | 约 43 分钟 |
| 插图派生数据（含问题四不收缩对照解） | 约 12 分钟 |
| 40 张插图 + 版面自检 | 约 1.5 分钟 |
| 数据自检（347 项） | 约 1.5 分钟 |

对照实验那一步占了大头（$N=400$ 的一阶格式要一步步推到 61 h），
它只服务于论文里的收敛性与口径论证；只要四个 result 文件的话跑 `--fast` 就够。

---

## 三、目录结构

```
药材烘干-代码与数据/
├── README.md                     本文件
├── requirements.txt              四个依赖（含版本下限）
├── requirements-lock.txt         出包时实测通过的精确版本
├── setup.sh                      建 .venv + 装依赖 + 环境自检
├── reproduce.sh                  一键复现（--fast 只跑四个 result 文件）
│
├── A题-药材的烘干问题.md          题面全文转写（含 6 张表与附录公式）
├── A题-药材的烘干问题.pdf         题面原始 PDF
├── 附件/                         附件 1（烘房温度与水分浓度）、附件 2（药材半径）
├── 模板/                         附件 3 的 result1-4.xlsx 原始模板（尺寸参考）
│
├── 代码/
│   ├── solve_p1.py               问题一求解器（常数物性、热质解耦）
│   ├── solve_p234.py             问题二/三/四求解器（变物性、耦合迭代、贴体坐标）
│   ├── run_all.py                求解问题二/三/四并导出 result{23,4}_data.npz
│   ├── prepare_outputs.py        把解整理成 result2/3/4.bin（题面要求的时间间隔）
│   ├── build_result1.py          写 result1.xlsx
│   ├── build_results234.py       写 result3/4.xlsx
│   ├── build_result2_xlsx.py     写 result2.xlsx（流式，910 万格）
│   ├── xlsx_style.py             四张表的统一样式（附件 3 模板格式）
│   ├── paper_tables.py           导出正文表 3-表 6（Markdown）
│   ├── p23_variants.py           网格 N / 时间步 / 口径 的 20 组对照
│   ├── closure_rhod.py           第三种口径（干基密度守恒）补齐 + 三种口径对照 CSV
│   ├── sens.py                   传热、传质系数与扩散系数正负 20% 的灵敏度
│   ├── shrink_criterion.py       收缩判据与代价（斜率截距比 r=b/a）
│   ├── prepare_figure_data.py    插图所需的全部派生数据 → 输出/figdata/
│   ├── make_figures.py           40 张插图（含出图自检闭环）
│   ├── verify_paper_numbers.py   数据自检：把每个可核验的数字重算一遍
│   ├── export_baseline_tables.py 导出基准值（表 1-表 6）供上面那个脚本比对
│   ├── check_env.py              环境自检（解释器 / 依赖 / 中文字体）
│   ├── 代码导读.md               逐段讲解两个求解器
│   └── figlib/                   插图样式模块 + 出图自检模块（来源与许可见 NOTICE.md）
│
├── 输出/                         全部结果（提交用的四张表就在这里）
│   ├── result1.xlsx ~ result4.xlsx
│   ├── 问题一-表1表2.md、问题二三四-表格.md、问题三-网格与口径对照.csv、
│   │   问题三-三种口径对照.csv、收缩判据与代价.json、数据自检报告.json
│   ├── figs/                     40 张插图（矢量 PDF + 300 dpi PNG + 灰度预览）
│   └── figdata/                  插图派生数据（附件 CSV、对照解、灵敏度、阈值扫描）
│
└── 补充分析/斜率截距与收缩/        收缩判据的专题分析（脚本 + 数据 + 分析稿）
```

---

## 四、每个产物是谁生成的

| 产物 | 生成脚本 | 依赖的输入 |
| --- | --- | --- |
| `输出/result1.xlsx` | `代码/solve_p1.py` → `代码/build_result1.py` | 附件 1、附录 2 物性（题面给出） |
| `输出/result2.xlsx` | `代码/run_all.py` → `prepare_outputs.py` → `build_result2_xlsx.py` | 附件 1、附录 3 物性 |
| `输出/result3.xlsx` | `代码/run_all.py` → `prepare_outputs.py` → `build_results234.py 3` | 同上（无收缩） |
| `输出/result4.xlsx` | `代码/run_all.py` → `prepare_outputs.py` → `build_results234.py 4` | 附件 1、附件 2、附录 4 物性 |
| `输出/问题一-表1表2.md` | `代码/solve_p1.py --tables` | 问题一解 |
| `输出/问题二三四-表格.md` | `代码/paper_tables.py` | result1-4.xlsx |
| `输出/问题三-网格与口径对照.csv` | `代码/p23_variants.py --table` | 按网格、时间步、口径重解 20 次 |
| `输出/问题三-三种口径对照.csv` | `代码/closure_rhod.py --all` | 按三种口径重解 6 次 |
| `输出/收缩判据与代价.json` | `代码/shrink_criterion.py` | 题面物性 + 附件 2 实测半径 |
| `输出/figdata/*` | `代码/prepare_figure_data.py` | 附件 1、附件 2 + 问题一和问题四重解 |
| `输出/figs/*` | `代码/make_figures.py` | `输出/` 与 `输出/figdata/` 的结果文件 |
| `输出/数据自检报告.json` | `代码/verify_paper_numbers.py --json` | 上面全部产物 |

**绘图脚本不硬编码任何结论数字**：数据图里的每一个数都从 `输出/` 的结果文件读，
所以"图"与"表"必然同源。

---

## 五、自检：凭什么相信这些数

```bash
./.venv/bin/python 代码/verify_paper_numbers.py --json 输出/数据自检报告.json
```

这条命令把论文里每个可核验的数字重算一遍，并列成"基准值 vs 复算值"的对照，
任何一条不一致都会被标出来（基准值取自 `输出/基准值-论文表1到表6.json`，
内容就是论文表 1 到表 6，由 `代码/export_baseline_tables.py` 从论文源文件导出）。
包内已经验证过的关键检验：

* **守恒性**：问题一水分守恒残差 6.8e-14（机器精度）；
* **交叉验证**：问题二求解器换成附录 2 物性后，与问题一独立求解器的温度场
  最大偏差 2.6e-12 摄氏度；
* **网格收敛**：N=20/50/100/200/400 的烘干时间 56.482/57.118/57.324/57.417/57.456 h，
  增量逐次减半（一阶收敛）；
* **时间步收敛**：N=100 下时间步 2 到 120 s 只改 0.17%；
* **口径敏感性**：把体积密度写回水分方程会使烘干时长增加 6.3%，
  该差值在 20 组网格与时间步组合下保持不变，说明它来自模型口径而不是数值实现；
* **四个 result 文件**：与论文表 1 到表 6 逐格一致。

---

## 六、环境与可移植性

* **Python 3.9 及以上**；依赖只有 numpy、openpyxl、matplotlib、seaborn。
* **不需要 Node.js 或 npm**：原版 `build_result1.mjs`、`build_results234.mjs` 依赖
  `@oai/artifact-tool`，本包已用 openpyxl 重写为 `build_result1.py`、
  `build_results234.py`、`build_result2_xlsx.py`，四张表的数值逐格一致。
* **不需要 Codex**：出图自检用到的 `export_figure.py`、`visual_qa.py` 已复制进
  `代码/figlib/`（来源与许可见 `代码/figlib/NOTICE.md`）。
* **不需要联网**：除 `setup.sh` 装依赖那一步外，全部计算离线完成。
  离线机器可以先把 wheel 包下好再拷过去：
  `pip download -r requirements.txt -d wheels/`，
  然后在目标机执行
  `./.venv/bin/pip install --no-index --find-links wheels -r requirements.txt`。
* **中文字体**：插图里有中文标签。macOS 上 `Arial Unicode MS`（Office 自带）或
  `Songti SC` 都可以；Linux 装 `fonts-noto-cjk`；Windows 自带 `SimHei`。
  一个中文字体都没有时 `代码/check_env.py` 会直接报错（否则图里的中文会变成方框）。
* **matplotlib 版本差异**会让插图的像素级外观略有不同（换行位置、字体度量），
  但数据与四个 xlsx 不受影响。出包时实测的版本见 `requirements-lock.txt`。
* 生成论文 PDF 需要 LaTeX（Tectonic 或 TeX Live），与数据复现无关，本包也不含论文。

---

## 七、不入库的大文件与中间产物

`.gitignore` 排除了几类可以由脚本重新生成的大文件，仓库因此保持在可推送的体量：

| 文件 | 体积 | 重新生成方式 |
| --- | --- | --- |
| `输出/result2.bin`、`result3.bin`、`result4.bin` | 72 MB | `代码/run_all.py` + `代码/prepare_outputs.py` |
| `输出/result23_data.npz` 等求解缓存 | 13 MB | 同上，或 `代码/solve_p1.py` |
| `输出/figdata/p4_noshrink.npz` | 135 MB（超 GitHub 单文件上限） | `代码/prepare_figure_data.py` |
| `输出/*.inspect.ndjson` | 63 MB | 旧版 artifact-tool 的检查转储，本包不再生成 |

---

## 八、已知取舍

* `result2.xlsx` 有 206700 行、22 列、2 张表（约 910 万格），约 27 MB，
  用 openpyxl 的流式模式写入，峰值内存与行数无关；列宽、冻结窗格与网格线由脚本
  在保存后补写工作表 XML 得到。
* 问题四中半径收缩到某位置以下后，该固定位置的水分浓度无定义，
  `result4.xlsx` 的相应单元格留空（不是 0）。
* 题面未给出的三处闭合关系（传质边界条件的密度口径、汽化潜热是否计入、
  水分方程用经典 Fick 还是把体积密度写回）在 `代码/p23_variants.py`、
  `代码/closure_rhod.py` 与 `补充分析/` 里分别定量给出，论文正文据此选择经典
  Fick 口径并作敏感性说明。
* 题目自带的输出网格（N=20）烘干时间为 56.48 h，比 N=400 的收敛值低 1.6%，
  不能当求解网格用；正文一律按 N=200 报告。

---

## 九、怎么读代码

两个求解器都带详细注释（每个函数的数学推导、每个系数的来历、容易写错的地方），
配套的逐段讲解见 [`代码/代码导读.md`](代码/代码导读.md)：

* `solve_p1.py`：常量 → 控制体权重 → 追赶法 → 温度步 → 水分步 → 主循环 → 守恒检验；
* `solve_p234.py` 与问题一的关键差别：变物性、耦合迭代、贴体坐标与问题四的对流项；
* 自己验证代码正确性的四种手段，以及改动后的自检顺序。

补充说明：`代码/figlib/NOTICE.md` 记录了随包分发的第三方模块来源与许可
（mathmodel-kit 的插图样式，Apache-2.0；scipilot-figure-skill 的出图自检，MIT）。
