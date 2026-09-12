#!/usr/bin/env bash
# 建立独立虚拟环境并安装依赖。
#
# 用法:
#   ./setup.sh                       # 默认用 python3 建 .venv
#   PYTHON=/usr/local/bin/python3.12 ./setup.sh
#   PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple ./setup.sh   # 国内镜像
#
# 装完之后所有脚本都用 ./.venv/bin/python 运行，不再依赖任何外部运行时
# （原项目里用于写 xlsx 的 Node + @oai/artifact-tool 依赖已全部移除，
# 改用 openpyxl 实现，见 代码/build_result1.py、代码/build_results234.py、
# 代码/build_result2_xlsx.py）。
set -euo pipefail

cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "找不到 ${PYTHON}，请用 PYTHON=/path/to/python3 ./setup.sh 指定解释器" >&2
  exit 1
fi

echo "使用解释器: $("$PYTHON" -c 'import sys; print(sys.executable)')"
echo "Python 版本: $("$PYTHON" -V)"

if [ ! -d .venv ]; then
  echo "==> 建立虚拟环境 .venv"
  "$PYTHON" -m venv .venv
fi

echo "==> 安装依赖（numpy / openpyxl / matplotlib / seaborn）"
if [ -n "${PIP_INDEX_URL:-}" ]; then
  ./.venv/bin/python -m pip install -q -r requirements.txt -i "$PIP_INDEX_URL"
else
  ./.venv/bin/python -m pip install -q -r requirements.txt
fi

echo "==> 环境自检"
./.venv/bin/python 代码/check_env.py

echo
echo "完成。下一步："
echo "  ./reproduce.sh        # 一键复现全部数据（含插图，约 60 分钟）"
echo "  ./reproduce.sh --fast # 只复现四个 result 文件（约 8 分钟）"
