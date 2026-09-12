#!/usr/bin/env bash
# 一键复现全部数据。
#
#   ./reproduce.sh          # 全量：四个 result 文件 + 对照实验 + 派生数据 + 插图（约 30~50 分钟）
#   ./reproduce.sh --fast   # 只复现四个 result 文件与正文表格（约 5~8 分钟）
#
# 前置：先跑 ./setup.sh（建 .venv 装 numpy / openpyxl / matplotlib）。
# 脚本只写 输出/ 目录，不会动 附件/ 与代码。
set -euo pipefail

cd "$(dirname "$0")"
PY="${PY:-./.venv/bin/python}"
FAST=0
[ "${1:-}" = "--fast" ] && FAST=1
export PYTHONUNBUFFERED=1        # 让每一步的进度实时可见（否则管道里会被缓冲）

# 对照实验的并行进程数：默认按本机核数，可用 JOBS=6 ./reproduce.sh 覆盖
JOBS="${JOBS:-$( (command -v nproc >/dev/null 2>&1 && nproc) \
  || sysctl -n hw.ncpu 2>/dev/null || echo 4 )}"

if [ ! -x "$PY" ]; then
  echo "找不到 ${PY}，请先执行 ./setup.sh" >&2
  exit 1
fi

t0=$(date +%s)
step() {
  echo
  echo "=============================================================="
  echo "[$(date +%H:%M:%S)] $*"
  echo "=============================================================="
}
elapsed() {
  local now; now=$(date +%s)
  echo "---- 累计用时 $(( (now - t0) / 60 )) 分 $(( (now - t0) % 60 )) 秒"
}

mkdir -p 输出

step "0/6 环境自检"
$PY 代码/check_env.py

step "1/6 问题一：求解 + 生成 result1.xlsx 与正文表 1、表 2"
$PY 代码/solve_p1.py --save 输出/result1_data.npz --tables 输出/问题一-表1表2.md
$PY 代码/build_result1.py
elapsed

step "2/6 问题二/三/四：求解（N=200, dt=5 s）"
$PY 代码/run_all.py --n 200 --dt 5
$PY 代码/prepare_outputs.py
$PY 代码/build_results234.py
$PY 代码/build_result2_xlsx.py       # 大表流式写入，约 3 分钟
$PY 代码/paper_tables.py
elapsed

if [ "$FAST" = "0" ]; then
  step "3/6 对照实验：网格 / 时间步 / 水分方程口径"
  $PY 代码/p23_variants.py --table --jobs "$JOBS" --csv 输出/问题三-网格与口径对照.csv
  $PY 代码/closure_rhod.py --all
  $PY 代码/sens.py
  $PY 代码/shrink_criterion.py --analytic --matrix --sweep --jobs "$JOBS"
  elapsed

  step "4/6 插图派生数据（问题一细网格解、不收缩对照、阈值扫描等，约 12 分钟）"
  $PY 代码/prepare_figure_data.py
  elapsed

  step "5/6 生成全部插图（矢量 PDF + 300 dpi PNG + 灰度预览 + 版面自检）"
  $PY 代码/make_figures.py
  elapsed
else
  step "3~5/6 跳过对照实验与插图（--fast）"
fi

step "6/6 数据自检：重算论文里每个可核验的数字并与基准值比对"
if [ "$FAST" = "0" ]; then
  $PY 代码/verify_paper_numbers.py --json 输出/数据自检报告.json
else
  echo "（--fast 模式下部分基准值（对照 CSV、figdata）不存在，只跑轻量项）"
  $PY 代码/verify_paper_numbers.py --json 输出/数据自检报告.json || true
fi

step "完成"
elapsed
echo
echo "主要产物:"
ls -lh 输出/result1.xlsx 输出/result2.xlsx 输出/result3.xlsx 输出/result4.xlsx
