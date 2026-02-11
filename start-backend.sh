#!/bin/bash
# 后端服务启动脚本

set -e

# 项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 日志目录
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

# 日志文件（带时间戳）
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/server_$TIMESTAMP.log"

# 同时输出到最新日志
LATEST_LOG="$LOG_DIR/server_latest.log"
ln -sf "$LOG_FILE" "$LATEST_LOG"

echo "=========================================="
echo "后端服务启动中..."
echo "日志文件: $LOG_FILE"
echo "=========================================="

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker 未运行，请先启动 Docker 或 OrbStack"
    echo "然后执行: docker compose up -d"
    exit 1
fi

# 启动 Docker 服务
echo "启动 Docker 服务..."
docker compose up -d postgres minio

# 等待数据库就绪
echo "等待数据库启动..."
sleep 3

# 停止旧的后端进程
echo "停止旧的后端进程..."
pkill -f "uvicorn app.api.main" || true
sleep 1

# 启动后端
echo "启动后端服务..."
.venv/bin/python -m uvicorn app.api.main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --log-level info \
    --access-log \
    --no-use-colors \
    >> "$LOG_FILE" 2>&1 &

BACKEND_PID=$!

# 等待服务启动
sleep 3

# 检查服务状态
if ps -p $BACKEND_PID > /dev/null; then
    echo "=========================================="
    echo "后端服务启动成功!"
    echo "PID: $BACKEND_PID"
    echo "端口: 8001"
    echo "日志: $LATEST_LOG"
    echo ""
    echo "查看实时日志:"
    echo "  tail -f $LATEST_LOG"
    echo ""
    echo "停止服务:"
    echo "  kill $BACKEND_PID"
    echo "=========================================="

    # 显示最新日志
    echo ""
    echo "--- 最新日志 ---"
    tail -20 "$LATEST_LOG"
else
    echo "=========================================="
    echo "后端服务启动失败!"
    echo "查看日志: $LOG_FILE"
    echo "=========================================="
    cat "$LATEST_LOG"
    exit 1
fi
