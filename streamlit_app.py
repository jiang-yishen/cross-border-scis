"""
跨境海外仓供应链智能决策系统 - 诊断版本
=========================================
先确认环境正常，再逐步恢复功能
"""
import streamlit as st
import os
import sys

st.set_page_config(page_title="SC-Decision 诊断", layout="wide")

st.title("🔧 环境诊断")

# 1. 当前工作目录
st.subheader("1. 工作目录")
cwd = os.getcwd()
st.code(f"cwd = {cwd}")

# 2. 文件列表
st.subheader("2. 文件列表")
try:
    files = os.listdir(cwd)
    st.code(f"文件数: {len(files)}\n" + "\n".join(files[:50]))
except Exception as e:
    st.error(f"列出文件失败: {e}")

# 3. 检查 data.db
st.subheader("3. data.db 检查")
db_path = os.path.join(cwd, "data.db")
st.code(f"db_path = {db_path}")
st.code(f"db_exists = {os.path.exists(db_path)}")
if os.path.exists(db_path):
    st.code(f"db_size = {os.path.getsize(db_path) / 1024**2:.2f} MB")

# 4. 检查 data 目录
st.subheader("4. data/ 目录检查")
data_dir = os.path.join(cwd, "data")
st.code(f"data_dir_exists = {os.path.exists(data_dir)}")
if os.path.exists(data_dir):
    data_files = os.listdir(data_dir)
    st.code(f"data文件数: {len(data_files)}\n" + "\n".join(data_files))

# 5. 检查 Python 版本
st.subheader("5. Python 版本")
st.code(f"Python {sys.version}")

# 6. 尝试导入关键库
st.subheader("6. 库导入测试")
try:
    import pandas as pd
    st.success("✅ pandas 导入成功")
except Exception as e:
    st.error(f"❌ pandas 导入失败: {e}")

try:
    import plotly
    st.success("✅ plotly 导入成功")
except Exception as e:
    st.error(f"❌ plotly 导入失败: {e}")

try:
    import sqlite3
    st.success("✅ sqlite3 导入成功")
except Exception as e:
    st.error(f"❌ sqlite3 导入失败: {e}")

# 7. 尝试连接 data.db
st.subheader("7. SQLite 连接测试")
if os.path.exists(db_path):
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        conn.close()
        st.success(f"✅ SQLite 连接成功")
        st.code(f"表列表: {tables}")
    except Exception as e:
        st.error(f"❌ SQLite 连接失败: {e}")
else:
    st.warning("⚠️ data.db 不存在，跳过 SQLite 测试")

# 8. 尝试导入 utils.py
st.subheader("8. utils.py 导入测试")
try:
    import utils
    st.success("✅ utils.py 导入成功")
    st.code(f"USE_SQLITE = {utils.USE_SQLITE}")
    st.code(f"DB_PATH = {utils.DB_PATH}")
except Exception as e:
    st.error(f"❌ utils.py 导入失败: {e}")
    import traceback
    st.code(traceback.format_exc())

# 9. 尝试导入 components.py
st.subheader("9. components.py 导入测试")
try:
    import components
    st.success("✅ components.py 导入成功")
except Exception as e:
    st.error(f"❌ components.py 导入失败: {e}")
    import traceback
    st.code(traceback.format_exc())

st.markdown("---")
st.info("诊断完成。如果以上全部显示 ✅，说明环境正常，可以恢复完整功能。")
