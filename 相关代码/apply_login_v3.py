import paramiko
import base64

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 直接在服务器上创建修改脚本（避免本地引号问题）
script = """
import re
with open('/opt/scis/streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加用户配置
marker1 = 'from components import sidebar_navigation, set_page_config, apply_custom_css'
user_cfg = marker1 + '''\n\n# === 用户权限配置 ===\nUSERS = {\n    \"admin\":   {\"password\": \"jwyjys5210\", \"role\": \"admin\",   \"name\": \"系统管理员\"},\n    \"planner\": {\"password\": \"scis2024\", \"role\": \"planner\", \"name\": \"计划主管\"},\n    \"viewer\":  {\"password\": \"scis2024\", \"role\": \"viewer\",  \"name\": \"业务查看员\"},\n}\n\nROLE_PERMISSIONS = {\n    \"admin\":   [\"home\",\"import\",\"forecast\",\"inventory\",\"replenish\",\"transfer\",\"logistics\",\"guide\",\"ops\"],\n    \"planner\": [\"home\",\"import\",\"forecast\",\"inventory\",\"replenish\",\"transfer\",\"logistics\",\"guide\"],\n    \"viewer\":  [\"home\",\"guide\"],\n}\n\nROLE_ICONS = {\"admin\": \"👑\", \"planner\": \"👤\", \"viewer\": \"🔍\"}\n'''

if marker1 in content:
    content = content.replace(marker1, user_cfg, 1)
    print("OK: user_config")
else:
    print("FAIL: user_config")

# 2. 替换 main() 函数
old_main = '''def main():\n    \"\"\"主入口：初始化 + 页面路由\"\"\"\n    set_page_config()\n    apply_custom_css()\n    \n    selected_page = sidebar_navigation()\n    \n    if selected_page == \"🏠 首页仪表盘\":\n        page_home()'''

new_main = '''def page_login():\n    st.markdown(\"\"\"<style>[data-testid=\\\"stSidebar\\\"] {display: none !important;}</style>\"\"\", unsafe_allow_html=True)\n    c1, c2 = st.columns([1, 1])\n    with c1:\n        st.markdown(\"\"\"<div style=\\\"display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;min-height:500px;background:linear-gradient(135deg,#1B4965 0%,#457B9D 100%);border-radius:16px;padding:40px;color:white;text-align:center;\\\"><div style=\\\"font-size:64px;margin-bottom:20px;\\\">🚢</div><h1 style=\\\"color:white;margin:0 0 12px 0;font-size:28px;\\\">跨境海外仓</h1><h2 style=\\\"color:white;margin:0 0 16px 0;font-size:20px;opacity:0.9;\\\">供应链智能决策系统</h2><div style=\\\"margin-top:32px;display:flex;gap:24px;justify-content:center;\\\"><div style=\\\"text-align:center;\\\"><div style=\\\"font-size:24px;font-weight:700;\\\">1,100+</div><div style=\\\"font-size:12px;opacity:0.7;\\\">SKU覆盖</div></div><div style=\\\"text-align:center;\\\"><div style=\\\"font-size:24px;font-weight:700;\\\">6</div><div style=\\\"font-size:12px;opacity:0.7;\\\">海外仓库</div></div><div style=\\\"text-align:center;\\\"><div style=\\\"font-size:24px;font-weight:700;\\\">2026</div><div style=\\\"font-size:12px;opacity:0.7;\\\">系统版本</div></div></div></div>\"\"\", unsafe_allow_html=True)\n    with c2:\n        st.markdown(\"<div style='height:60px;'></div>\", unsafe_allow_html=True)\n        st.markdown(\"\"\"<div style=\\\"text-align:center;margin-bottom:24px;\\\"><div style=\\\"font-size:36px;margin-bottom:8px;\\\">🔐</div><h2 style=\\\"color:#1B4965;margin:0;font-size:22px;\\\">欢迎登录</h2><p style=\\\"color:#6B7280;margin:4px 0 0 0;font-size:13px;\\\">请输入您的账号和密码</p></div>\"\"\", unsafe_allow_html=True)\n        with st.form(\"login_form\"):\n            username = st.text_input(\"用户名\", placeholder=\"请输入用户名\")\n            password = st.text_input(\"密码\", type=\"password\", placeholder=\"请输入密码\")\n            submitted = st.form_submit_button(\"🚀 登录\", use_container_width=True, type=\"primary\")\n            if submitted:\n                if username in USERS and USERS[username][\"password\"] == password:\n                    st.session_state.user_logged_in = True\n                    st.session_state.user_info = {\"username\": username, \"name\": USERS[username][\"name\"], \"role\": USERS[username][\"role\"]}\n                    st.success(f\"✅ 欢迎回来，{USERS[username]['name']}！\")\n                    st.rerun()\n                else:\n                    st.error(\"❌ 用户名或密码错误\")\n        st.markdown(\"\"\"<div style=\\\"background:#F8FAFC;border-radius:10px;padding:16px;margin-top:16px;border:1px dashed #CBD5E1;\\\"><p style=\\\"color:#1B4965;font-weight:600;margin:0 0 8px 0;font-size:13px;\\\">🎮 试玩账号</p><div style=\\\"display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px;color:#4B5563;\\\"><div><b>admin</b> / jwyjys5210</div><div><span style=\\\"color:#9CA3AF;\\\">管理员·全权限</span></div><div><b>planner</b> / scis2024</div><div><span style=\\\"color:#9CA3AF;\\\">计划员·运营模块</span></div><div><b>viewer</b> / scis2024</div><div><span style=\\\"color:#9CA3AF;\\\">查看员·只读权限</span></div></div></div>\"\"\", unsafe_allow_html=True)\n\n\ndef main():\n    set_page_config()\n    apply_custom_css()\n    if \"user_logged_in\" not in st.session_state:\n        st.session_state.user_logged_in = False\n    if \"user_info\" not in st.session_state:\n        st.session_state.user_info = None\n    if not st.session_state.get(\"user_logged_in\", False):\n        page_login()\n        return\n    selected_page = sidebar_navigation()\n    if selected_page == \"🏠 首页仪表盘\":\n        page_home()'''

if old_main in content:
    content = content.replace(old_main, new_main, 1)
    print("OK: login + main")
else:
    print("FAIL: main")

with open('/opt/scis/streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("DONE")
"""

# 用 base64 传输脚本到服务器
encoded = base64.b64encode(script.encode('utf-8')).decode('ascii')
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /tmp/fix_login_v3.py && python3 /tmp/fix_login_v3.py')
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')
print("=== 输出 ===")
print(out)
if err.strip():
    print("=== 错误 ===")
    print(err)

client.exec_command('sudo systemctl restart scis-streamlit')
print("\n🔄 服务已重启")

client.close()
