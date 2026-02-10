#!/usr/bin/env python3
import sys
from pathlib import Path
# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing imports...")
try:
    from app.api.main import create_app
    print("SUCCESS: create_app imported")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
