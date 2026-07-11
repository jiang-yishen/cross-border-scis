"""
PythonAnywhere WSGI 入口文件
用于将 Streamlit 应用部署到 PythonAnywhere 公网
==============================================
原理：在 PythonAnywhere 的 Web 应用中使用 Flask 代理请求到 Streamlit 的 Tornado 服务器
"""
import sys
import os
import subprocess
import time

# =============================================================================
# 1. 添加项目路径
# =============================================================================
# 注意：将下面的路径替换为您的 PythonAnywhere 用户名和项目路径
# 格式：/home/<您的用户名>/supply-chain
PROJECT_PATH = '/home/18943571672jys/supply-chain'
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# 添加项目内的子目录（数据文件路径）
DATA_PATH = os.path.join(PROJECT_PATH, 'data')
OUTPUT_PATH = os.path.join(PROJECT_PATH, 'output')

# =============================================================================
# 2. 启动 Streamlit 服务（如果尚未启动）
# =============================================================================
PID_FILE = '/tmp/streamlit_supply_chain.pid'

streamlit_started = False
if os.path.exists(PID_FILE):
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        # 检查进程是否仍在运行
        os.kill(pid, 0)
        streamlit_started = True
    except (ValueError, ProcessLookupError, OSError):
        streamlit_started = False

if not streamlit_started:
    # 启动 Streamlit 作为后台进程
    proc = subprocess.Popen(
        [
            sys.executable, '-m', 'streamlit', 'run',
            os.path.join(PROJECT_PATH, 'streamlit_app.py'),
            '--server.headless', 'true',
            '--server.port', '8501',
            '--server.address', '127.0.0.1',
            '--server.enableCORS', 'false',
            '--server.enableXsrfProtection', 'false',
            '--server.maxUploadSize', '5',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    with open(PID_FILE, 'w') as f:
        f.write(str(proc.pid))
    # 等待 Streamlit 启动
    time.sleep(8)

# =============================================================================
# 3. Flask 代理应用（将 HTTP 请求转发到 Streamlit）
# =============================================================================
from flask import Flask, request, Response, redirect
import requests

app = Flask(__name__)

STREAMLIT_BASE_URL = 'http://127.0.0.1:8501'


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """将请求代理到 Streamlit 服务器"""
    try:
        # 构建目标 URL
        target_url = f'{STREAMLIT_BASE_URL}/{path}'
        if request.query_string:
            target_url += '?' + request.query_string.decode()

        # 转发请求
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={k: v for k, v in request.headers if k.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30,
        )

        # 处理重定向（将内部地址替换为公网地址）
        if resp.status_code in (301, 302, 303, 307, 308):
            location = resp.headers.get('Location', '')
            # 不需要替换，因为浏览器会处理相对路径
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            headers = [(name, value) for name, value in resp.headers.items()
                       if name.lower() not in excluded_headers]
            return Response('', resp.status_code, headers)

        # 返回响应
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in resp.headers.items()
                   if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)

    except requests.exceptions.ConnectionError:
        # Streamlit 可能还在启动中
        return Response(
            '<html><head><meta http-equiv="refresh" content="3"></head>'
            '<body><h1>Streamlit 正在启动中...</h1><p>请等待 10-15 秒后刷新页面。</p></body></html>',
            200,
            [('Content-Type', 'text/html')]
        )
    except Exception as e:
        return Response(f'Error: {str(e)}', 500)


# WSGI 应用入口
application = app
