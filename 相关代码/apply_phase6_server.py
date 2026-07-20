import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 在服务器上创建修改脚本
script = r'''
import re

with open('/opt/scis/components.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在 NAV_PAGES 定义后添加用户配置
insert_after = 'NAV_PAGES = []\nfor g in NAV_GROUPS:\n    NAV_PAGES.extend(g["pages"])'

user_config = '''

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

ROLE_ICONS = {"admin": "👑", "planner": "👤", "viewer": "🔍"}


def get_user():
    return st.session_state.get("user_info")

def is_logged_in():
    return st.session_state.get("user_logged_in", False) is True

def get_allowed_pages():
    user = get_user()
    if not user:
        return []
    role = user.get("role", "viewer")
    allowed_keys = set(ROLE_PERMISSIONS.get(role, []))
    return [p for p in NAV_PAGES if p["key"] in allowed_keys]

'''

if insert_after in content:
    content = content.replace(insert_after, insert_after + user_config, 1)
    print("OK: user_config")
else:
    print("FAIL: user_config")

# 2. 在Logo区域后添加用户登录区
old_logo = '                SC-Decision Engine v1.0\n            </div>\n        </div>\n        """, unsafe_allow_html=True)\n\n        # 初始化 session state'

new_logo = '''                SC-Decision Engine v1.0
            </div>
        </div>
        """, unsafe_allow_html=True)

        # -- 用户登录区域 --
        _user = st.session_state.get("user_info")
        _logged_in = st.session_state.get("user_logged_in", False)
        if _logged_in and _user:
            _role_icon = ROLE_ICONS.get(_user["role"], "👤")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1B4965 0%, #457B9D 100%);
                        border-radius: 12px; padding: 16px; margin-bottom: 16px;
                        color: white; text-align: center;">
                <div style="font-size: 36px; margin-bottom: 8px;">{_role_icon}</div>
                <div style="font-weight: 600; font-size: 15px; margin-bottom: 2px;">{_user["name"]}</div>
                <div style="font-size: 12px; opacity: 0.85;">@{_user["role"]} | {_user["username"]}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚪 退出登录", use_container_width=True, key="sidebar_logout_btn"):
                st.session_state.user_logged_in = False
                st.session_state.user_info = None
                st.session_state.nav_page = None
                st.rerun()
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #F8FAFC; border-radius: 12px; padding: 16px; margin-bottom: 16px;
                        text-align: center; border: 1.5px dashed #CBD5E1;">
                <div style="font-size: 28px; margin-bottom: 8px;">🔒</div>
                <div style="font-weight: 600; color: #1B4965; font-size: 14px; margin-bottom: 4px;">未登录</div>
                <div style="font-size: 12px; color: #9CA3AF;">请登录以访问系统</div>
            </div>
            """, unsafe_allow_html=True)
            return None

        # 初始化 session state'''

if old_logo in content:
    content = content.replace(old_logo, new_logo, 1)
    print("OK: user_area")
else:
    print("FAIL: user_area")

# 3. 修改导航循环
old_nav = '''        # 渲染分组导航
        for group in NAV_GROUPS:'''
new_nav = '''        # 获取当前用户可访问的页面
        allowed_pages = get_allowed_pages()
        allowed_keys = {p["key"] for p in allowed_pages}

        # 渲染分组导航（权限过滤）
        for group in NAV_GROUPS:'''

if old_nav in content:
    content = content.replace(old_nav, new_nav, 1)
    print("OK: nav_filter")
else:
    print("FAIL: nav_filter")

# 4. 添加分组过滤
old_group = '''            # 分组标题（居中 + 两侧装饰线）'''
new_group = '''            # 过滤该分组下允许的页面
            group_pages = [pg for pg in group["pages"] if pg["key"] in allowed_keys]
            if not group_pages:
                continue

            # 分组标题（居中 + 两侧装饰线）'''

if old_group in content:
    content = content.replace(old_group, new_group, 1)
    print("OK: group_filter")
else:
    print("FAIL: group_filter")

# 5. 修改内层循环
old_inner = '''            for pg in group["pages"]:'''
new_inner = '''            for pg in group_pages:'''

if old_inner in content:
    content = content.replace(old_inner, new_inner, 1)
    print("OK: inner_loop")
else:
    print("FAIL: inner_loop")

# 6. 修改返回
old_ret = '''        return st.session_state.nav_page'''
new_ret = '''        if allowed_pages:
            _current = st.session_state.get("nav_page")
            _valid = {f"{p['icon']} {p['title']}" for p in allowed_pages}
            if _current is None or _current not in _valid:
                st.session_state.nav_page = f"{allowed_pages[0]['icon']} {allowed_pages[0]['title']}"
            return st.session_state.nav_page
        return None'''

if old_ret in content:
    content = content.replace(old_ret, new_ret, 1)
    print("OK: return")
else:
    print("FAIL: return")

with open('/opt/scis/components.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("DONE")
'''

sftp = client.open_sftp()
with sftp.file('/tmp/fix_login.py', 'w') as f:
    f.write(script.encode('utf-8'))

stdin, stdout, stderr = client.exec_command('python3 /tmp/fix_login.py')
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')
print("=== 输出 ===")
print(out)
if err.strip():
    print("=== 错误 ===")
    print(err)

client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
