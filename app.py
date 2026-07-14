# app.py - Hugging Face Spaces 入口文件
# ============================================
# 本文件是 Hugging Face Spaces 的默认入口。
# 直接加载并执行 streamlit_app.py 的全部逻辑。
# ============================================

import sys
import os

# 确保当前目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接执行 streamlit_app.py 的内容
with open(os.path.join(os.path.dirname(__file__), "streamlit_app.py"), "r", encoding="utf-8") as f:
    code = f.read()
exec(code)
