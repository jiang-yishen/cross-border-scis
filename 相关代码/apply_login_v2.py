import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 在服务器上创建修改脚本
script = """
import re

with open('/opt/scis/streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在导入组件后添加用户配置
import_marker = 'from components import sidebar_navigation, set_page_config, apply_custom_css'
user_config = '''from components import sidebar_navigation, set_page_config, apply_custom_css

# =========================================================================
# 用户权限配置
# =========================================================================
USERS = {
    "admin":   {"password": "jwyjys5210", "role": "admin",   "name": "系统管理员"},
    "planner": {"password": "scis2024", "role": "planner", "name": "计划主管"},
    "viewer":  {"password": "scis2024", "role": "viewer",  "name": "业务查看员"},
}

ROLE_PERMISSIONS = {
    "admin":   ["home", "import", "forecast", "inventory", "replenish", "transfer", "logistics", "guide", "ops"],
    "planner": ["home", "import", "forecast", "inventory", "replenish", "transfer", "logistics", "guide"],
    "viewer":  ["home", "guide"],
}

ROLE_ICONS = {"admin": "👑", "planner": "👤", "viewer": "🔍"}'''

if import_marker in content:
    content = content.replace(import_marker, user_config, 1)
    print("OK: user_config")
else:
    print("FAIL: user_config")

# 2. 在 main() 之前添加 page_login()
main_marker = '''def main():
    """主入口：初始化 + 页面路由"""
    set_page_config()
    apply_custom_css()
    
    selected_page = sidebar_navigation()
    
    if selected_page == "🏠 首页仪表盘":
        page_home()'''

login_page = '''def page_login():
    """用户登录页面"""
    # 隐藏侧边栏（用CSS）
    st.markdown("""
    <style>[data-testid="stSidebar"] {display: none !important;}</style>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("""
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center;
                    height: 100%; min-height: 500px;
                    background: linear-gradient(135deg, #1B4965 0%, #457B9D 100%);
                    border-radius: 16px; padding: 40px; color: white;
                    text-align: center;">
            <div style="font-size: 64px; margin-bottom: 20px;">🚢</div>
            <h1 style="color: white; margin: 0 0 12px 0; font-size: 28px;">跨境海外仓</h1>
            <h2 style="color: white; margin: 0 0 16px 0; font-size: 20px; opacity: 0.9;">供应链智能决策系统</h2>
            <div style="margin-top: 32px; display: flex; gap: 24px; justify-content: center;">
                <div style="text-align: center;"><div style="font-size: 24px; font-weight: 700;">1,100+</div><div style="font-size: 12px; opacity: 0.7;">SKU覆盖</div></div>
                <div style="text-align: center;"><div style="font-size: 24px; font-weight: 700;">6</div><div style="font-size: 12px; opacity: 0.7;">海外仓库</div></div>
                <div style="text-align: center;"><div style="font-size: 24px; font-weight: 700;">2026</div><div style="font-size: 12px; opacity: 0.7;">系统版本</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="font-size: 36px; margin-bottom: 8px;">🔐</div>
            <h2 style="color: #1B4965; margin: 0; font-size: 22px;">欢迎登录</h2>
            <p style="color: #6B7280; margin: 4px 0 0 0; font-size: 13px;">请输入您的账号和密码</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            submitted = st.form_submit_button("🚀 登录", use_container_width=True, type="primary")
            
            if submitted:
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.user_logged_in = True
                    st.session_state.user_info = {
                        "username": username,
                        "name": USERS[username]["name"],
                        "role": USERS[username]["role"],
                    }
                    st.success(f"✅ 欢迎回来，{USERS[username]['name']}！")
                    st.rerun()
                else:
                    st.error("❌ 用户名或密码错误")
        
        st.markdown("""
        <div style="background: #F8FAFC; border-radius: 10px; padding: 16px; margin-top: 16px;
                    border: 1px dashed #CBD5E1;">
            <p style="color: #1B4965; font-weight: 600; margin: 0 0 8px 0; font-size: 13px;">🎮 试玩账号</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; color: #4B5563;">
                <div><b>admin</b> / jwyjys5210</div><div><span style="color: #9CA3AF;">管理员·全权限</span></div>
                <div><b>planner</b> / scis2024</div><div><span style="color: #9CA3AF;">计划员·运营模块</span></div>
                <div><b>viewer</b> / scis2024</div><div><span style="color: #9CA3AF;">查看员·只读权限</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """主入口：初始化 + 页面路由"""
    set_page_config()
    apply_custom_css()
    
    # 登录状态初始化
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    
    # 未登录 -> 显示登录页
    if not st.session_state.get("user_logged_in", False):
        page_login()
        return
    
    selected_page = sidebar_navigation()
    
    if selected_page == "🏠 首页仪表盘":
        page_home()'''

if main_marker in content:
    content = content.replace(main_marker, login_page, 1)
    print("OK: login_page + main")
else:
    print("FAIL: main")

# 3. 在 streamlit_app.py 最末尾，if __name__ == "__main__": 之后不需要修改

with open('/opt/scis/streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("DONE")
"""

sftp = client.open_sftp()
with sftp.file('/tmp/fix_login_v2.py', 'w') as f:
    f.write(script.encode('utf-8'))

stdin, stdout, stderr = client.exec_command('python3 /tmp/fix_login_v2.py')
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
