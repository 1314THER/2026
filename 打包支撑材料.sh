#!/usr/bin/env bash
# 把交付所需的支撑材料打成一个 ZIP（竞赛要求 ≤20 MB，文件名提交前改成校内编号）。
#
#   ./打包支撑材料.sh                  # 默认包（约 11 MB，不含 27 MB 的 result2.xlsx）
#   ./打包支撑材料.sh --with-result2   # 连 result2.xlsx 一起打（约 38 MB，会超 20 MB 限制）
#
# 排除的都是"可以由脚本重算"的大文件：求解中间产物（*.bin、*_data.npz）、
# 不收缩对照解（p4_noshrink.npz）、插图的 300 dpi PNG 预览（保留矢量 PDF）、
# 旧版 artifact-tool 的检查转储（*.inspect.ndjson）。
set -euo pipefail

cd "$(dirname "$0")"
WITH_RESULT2=0
[ "${1:-}" = "--with-result2" ] && WITH_RESULT2=1

OUT="支撑材料.zip"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

echo "==> 汇集文件到临时目录"
RSYNC_EXCL=(
  --exclude '论文/论文全文.pdf'
  --exclude '论文/论文全文_交付版.pdf'
  --exclude '论文/论文全文_缩放版.pdf'
  --exclude '输出/figs/*.png'
  --exclude '输出/figdata/p4_noshrink.npz'
  --exclude '输出/*.bin'
  --exclude '输出/*_data.npz'
  --exclude '输出/result1_data.json'
  --exclude '输出/*.inspect.ndjson'
  --exclude '__pycache__'
  --exclude '*.pyc'
  --exclude '.DS_Store'
  --exclude '.venv'
  --exclude '.git'
  --exclude '支撑材料.zip'
)
if [ "$WITH_RESULT2" = "0" ]; then
  RSYNC_EXCL+=(--exclude '输出/result2.xlsx')
fi

rsync -a "${RSYNC_EXCL[@]}" ./ "$STAGE/"

echo "==> 压缩"
rm -f "$OUT"
( cd "$STAGE" && zip -qr "$OLDPWD/$OUT" . )

size_mb=$(du -m "$OUT" | awk '{print $1}')
echo
echo "已生成: $OUT  (${size_mb} MB)"
echo
echo "包内主要条目:"
( cd "$STAGE" && find . -maxdepth 2 -type d | sed 's|^\./||' | grep -v '^\.$' | sort | head -20 )
echo
echo "逐目录体积:"
du -sh "$STAGE"/* 2>/dev/null | sed "s|$STAGE/||" | sort -h

echo
if [ "$size_mb" -le 20 ]; then
  echo "✅ 体积 ${size_mb} MB，符合 ≤20 MB 要求"
else
  echo "⚠️  体积 ${size_mb} MB，超过 20 MB。"
  if [ "$WITH_RESULT2" = "1" ]; then
    echo "    result2.xlsx 单独就有 27 MB（1 s 间隔、覆盖整个烘干过程，已是压缩格式）。"
    echo "    若提交系统允许，请把四个 result*.xlsx 单独上传；否则请去掉 --with-result2。"
  fi
fi
echo
echo "提交前：把本文件与 论文/论文全文_交付版.pdf 都改成校内编号（例：2026001.zip / 2026001.pdf），"
echo "        文件名中不要出现姓名、学校、赛区。"
