#!/bin/bash
# 测试服务器启动

# 切换到项目根目录（test 目录的上一级）
cd "$(dirname "$0")/.."

echo "=== 1. 检查 Python 版本 ==="
python3 --version

echo ""
echo "=== 2. 检查导入 ==="
python3 -c "from app.api.main import create_app; print('Import OK')"

echo ""
echo "=== 3. 启动服务器 ==="
uv run uvicorn app.api.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
