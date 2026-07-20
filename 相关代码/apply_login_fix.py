import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 1. 从 git 恢复（确保干净）
client.exec_command('cd /opt/scis && git checkout HEAD -- streamlit_app.py')

# 2. 读取内容
stdin, stdout, stderr = client.exec_command('cat /opt/scis/streamlit_app.py')
content = stdout.read().decode('utf-8')

# 3. 在 from components import (...) 的 ) 后面添加用户配置
marker = '    create_pie_chart, create_heatmap, apply_plotly_theme\n)'
user_cfg = '''    create_pie_chart, create_heatmap, apply_plotly_theme
)

# === User Auth Config ===
USERS = {
    "admin":   {"password": "jwyjys5210", "role": "admin",   "name": "Admin"},
    "planner": {"password": "scis2024", "role": "planner", "name": "Planner"},
    "viewer":  {"password": "scis2024", "role": "viewer",  "name": "Viewer"},
}

ROLE_PERMISSIONS = {
    "admin":   ["home","import","forecast","inventory","replenish","transfer","logistics","guide","ops"],
    "planner": ["home","import","forecast","inventory","replenish","transfer","logistics","guide"],
    "viewer":  ["home","guide"],
}

ROLE_ICONS = {"admin": "Crown", "planner": "User", "viewer": "Search"}'''

content = content.replace(marker, user_cfg, 1)
print("OK: user_config")

# 4. 在 "# 主入口" 前插入 page_login()
login_func = '''def page_login():
    st.markdown("<style>[data-testid=\\"stSidebar\\"] {display: none !important;}</style>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("<div style=\\"display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;min-height:500px;background:linear-gradient(135deg,#1B4965 0%,#457B9D 100%);border-radius:16px;padding:40px;color:white;text-align:center;\\\"><div style=\\"font-size:64px;margin-bottom:20px;\\\">🚢</div><h1 style=\\"color:white;margin:0 0 12px 0;font-size:28px;\\\">Cross-Border Warehouse</h1><h2 style=\\"color:white;margin:0 0 16px 0;font-size:20px;opacity:0.9;\\\">SCIS System</h2><div style=\\"margin-top:32px;display:flex;gap:24px;justify-content:center;\\\"><div style=\\"text-align:center;\\\"><div style=\\"font-size:24px;font-weight:700;\\\">1,100+</div><div style=\\"font-size:12px;opacity:0.7;\\\">SKUs</div></div><div style=\\"text-align:center;\\\"><div style=\\"font-size:24px;font-weight:700;\\\">6</div><div style=\\"font-size:12px;opacity:0.7;\\\">Warehouses</div></div><div style=\\"text-align:center;\\\"><div style=\\"font-size:24px;font-weight:700;\\\">2026</div><div style=\\"font-size:12px;opacity:0.7;\\\">Version</div></div></div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style=\\'height:60px;\\'></div>", unsafe_allow_html=True)
        st.markdown("<div style=\\"text-align:center;margin-bottom:24px;\\\"><div style=\\"font-size:36px;margin-bottom:8px;\\\">🔐</div><h2 style=\\"color:#1B4965;margin:0;font-size:22px;\\\">Welcome</h2><p style=\\"color:#6B7280;margin:4px 0 0 0;font-size:13px;\\\">Please login</p></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
            if submitted:
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.user_logged_in = True
                    st.session_state.user_info = {"username": username, "name": USERS[username]["name"], "role": USERS[username]["role"]}
                    st.success(f"Welcome, {USERS[username]['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        st.markdown("<div style=\\"background:#F8FAFC;border-radius:10px;padding:16px;margin-top:16px;border:1px dashed #CBD5E1;\\\"><p style=\\"color:#1B4965;font-weight:600;margin:0 0 8px 0;font-size:13px;\\\">Demo Accounts</p><div style=\\"display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px;color:#4B5563;\\\"><div><b>admin</b> / jwyjys5210</div><div><span style=\\"color:#9CA3AF;\\\">Full Access</span></div><div><b>planner</b> / scis2024</div><div><span style=\\"color:#9CA3AF;\\\">Planner</span></div><div><b>viewer</b> / scis2024</div><div><span style=\\"color:#9CA3AF;\\\">Read Only</span></div></div></div>", unsafe_allow_html=True)


'''

marker2 = '# =============================================================================\n# 主入口\n# ============================================================================='
content = content.replace(marker2, login_func + marker2, 1)
print("OK: login_func")

# 5. 修改 main()
old_part = '''    set_page_config()\n    apply_custom_css()\n    \n    # 侧边栏导航'''
new_part = '''    set_page_config()\n    apply_custom_css()\n    \n    # Login state init\n    if "user_logged_in" not in st.session_state:\n        st.session_state.user_logged_in = False\n    if "user_info" not in st.session_state:\n        st.session_state.user_info = None\n    \n    # Not logged in -> show login page\n    if not st.session_state.get("user_logged_in", False):\n        page_login()\n        return\n    \n    # 侧边栏导航'''

content = content.replace(old_part, new_part, 1)
print("OK: main_login")

# 6. 通过 sftp 写入
sftp = client.open_sftp()
with sftp.file('/opt/scis/streamlit_app.py', 'w') as f:
    f.write(content.encode('utf-8'))
print("OK: file written")

# 重启
client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
