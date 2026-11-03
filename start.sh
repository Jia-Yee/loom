#!/usr/bin/env bash
# Loom Loom AutoML 框架启动脚本
# 用法:
#   ./start.sh          # 命令行模式
#   ./start.sh web       # Web 控制台模式
#   ./start.sh history   # 查看历史

set -e

PYTHON="${PYTHON:-python3}"
MODE="${1:-cli}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================"
echo "  Loom — 可扩展 Loom AutoML 框架"
echo "================================================"
echo ""

# 检查依赖
echo "▶ 检查依赖..."
MISSING=""
for pkg in sklearn numpy openai flask; do
    if ! $PYTHON -c "import $pkg" 2>/dev/null; then
        MISSING="$MISSING $pkg"
    fi
done

if [ -n "$MISSING" ]; then
    echo "  缺少依赖:$MISSING"
    echo "  正在安装..."
    $PYTHON -m pip install -r requirements.txt 2>/dev/null || {
        echo "  ❌ 安装失败，请手动运行:"
        echo "     pip install -r requirements.txt"
        exit 1
    }
    echo "  ✅ 依赖安装完成"
else
    echo "  ✅ 依赖已就绪"
fi
echo ""

# 加载 .env
if [ -f .env ]; then
    echo "▶ 检测到 .env 配置文件"
    set -a
    source .env 2>/dev/null || true
    set +a
else
    echo "▶ 未检测到 .env（LLM 分析将跳过，训练评估正常执行）"
    echo "  如需 LLM 分析: cp .env.example .env && 编辑填入配置"
fi
echo ""

case "$MODE" in
    web)
        echo "▶ 启动 Web 控制台..."
        echo "  浏览器访问: http://localhost:5000"
        echo "  按 Ctrl+C 停止"
        echo ""
        exec $PYTHON server.py
        ;;
    history)
        exec $PYTHON main.py --history
        ;;
    cli|*)
        echo "▶ 启动命令行模式..."
        echo ""
        exec $PYTHON main.py
        ;;
esac
