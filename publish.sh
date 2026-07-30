#!/usr/bin/env bash
# 一键发布 HTML 到 GitHub Pages
# 用法:
#   ./publish.sh <html文件路径|file://链接>  [自定义线上文件名.html]
#   ./publish.sh --clipboard                  从剪贴板读取 file:// 链接
# 示例:
#   ./publish.sh ~/Desktop/orb-demo.html
#   ./publish.sh 'file:///Users/xx/outputs/foo.html'
#   ./publish.sh --clipboard

set -euo pipefail

# 让脚本能找到用户目录下安装的 gh / git
export PATH="$HOME/.local/bin:$PATH"

REPO_DIR="$HOME/voice-ui-demos"
PAGES_BASE="https://chenlanlan0401.github.io/voice-ui-demos"

# 把 file:// 链接 / URL 编码的路径 解码成真实本地路径
resolve_input() {
  local raw="$1"
  # 去掉首尾空白
  raw="$(printf '%s' "$raw" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  # file:// 前缀 + URL 解码
  python3 - "$raw" <<'PY'
import sys, urllib.parse
s = sys.argv[1]
if s.startswith("file://"):
    s = urllib.parse.urlparse(s).path
s = urllib.parse.unquote(s)
print(s)
PY
}

# ---- 参数检查 ----
if [ $# -lt 1 ]; then
  echo "❌ 用法: $0 <html文件路径|file://链接> [线上文件名.html]"
  echo "        $0 --clipboard   （从剪贴板读 file:// 链接）"
  exit 1
fi

# 支持 --clipboard：从剪贴板取链接
if [ "$1" = "--clipboard" ]; then
  CLIP="$(pbpaste)"
  if [ -z "$CLIP" ]; then echo "❌ 剪贴板是空的"; exit 1; fi
  set -- "$CLIP" "${2:-}"
fi

SRC="$(resolve_input "$1")"
if [ ! -f "$SRC" ]; then
  echo "❌ 找不到文件: $SRC"
  echo "   （原始输入: $1）"
  exit 1
fi

# ---- 决定线上文件名 ----
if [ $# -ge 2 ] && [ -n "$2" ]; then
  DEST_NAME="$2"
else
  DEST_NAME="$(basename "$SRC")"
fi

# 提醒：中文文件名在 URL 里会变成转义字符，不好复制
case "$DEST_NAME" in
  *[!\ -~]*) echo "⚠️  文件名含非英文字符，URL 会被转义，建议改用英文名（可作为第二个参数传入）。" ;;
esac

# 对文件名做 URL 编码（仅处理空格等常见情况的简单版）
ENC_NAME="${DEST_NAME// /%20}"
LINK="$PAGES_BASE/$ENC_NAME"

# ---- 复制 + 提交 + 推送 ----
cp "$SRC" "$REPO_DIR/$DEST_NAME"
cd "$REPO_DIR"
git add -A

if git diff --cached --quiet; then
  echo "ℹ️  内容与线上一致，无需重新发布（链接不变）。"
else
  git -c user.email="chenlanlan0401@users.noreply.github.com" \
      -c user.name="chenlanlan0401" \
      commit -q -m "发布/更新 $DEST_NAME"
  git push -q origin main
  echo "✅ 已推送，GitHub Pages 通常 1-2 分钟后生效。"
fi

# ---- 打印链接（无论是否新发布，都给出可分享链接）----
echo ""
echo "🔗 分享链接："
echo "   $LINK"
echo ""
echo "（把上面的链接粘进文档即可）"
