"""
PythonAnywhere 环境快速检测脚本
检查系统预装的包，避免重复安装
"""
import subprocess
import sys

# 检查已安装的包
print("=" * 60)
print("检测已安装的 Python 包...")
print("=" * 60)

check_packages = ['streamlit', 'pandas', 'plotly', 'numpy', 'openpyxl']

for pkg in check_packages:
    try:
        module = __import__(pkg)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {pkg:15s} 已安装 (v{version})")
    except ImportError:
        print(f"❌ {pkg:15s} 未安装")

print("\n" + "=" * 60)
print("Python 版本信息:")
print(f"Python {sys.version}")
print("=" * 60)
