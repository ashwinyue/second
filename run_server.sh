#!/bin/bash
# 启动服务器 (端口 8001)

cd /Users/mervyn/second

echo "=== 启动 DEAR Agent 服务器 ==="
echo "API 文档: http://localhost:8001/docs"
echo "健康检查: http://localhost:8001/api/v1/health"
echo ""

uv run uvicorn app.api.main:create_app --factory --host 0.0.0.0 --port 8001
