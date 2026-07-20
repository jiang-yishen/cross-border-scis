import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 清除之前的临时文件
client.exec_command('rm -f /tmp/fix_comp.py /tmp/fix_components.py')

# 在服务器上创建 Python 修改脚本（分多行写入避免引号冲突）
commands = [
    'cat > /tmp/fix_comp.py << \'PYEOF\'',
    'import re',
    '',
    'with open("/opt/scis/components.py", "r", encoding="utf-8") as f:',
    '    content = f.read()',
    '',
    '# 1. 添加用户配置在 NAV_PAGES 定义后',
    'insert_after = """NAV_PAGES = []\nfor g in NAV_GROUPS:\n    NAV_PAGES.extend(g["pages"])"""',
    '',
    'user_config = """\n\n# === 用户权限配置 ===\nUSERS = {',
    '    "admin":   {"password": "jwyjys5210", "role": "admin",   "name": "系统管理员"},',
    '    "planner": {"password": "scis2024", "role": "planner", "name": "计划主管"},',
    '    "viewer":  {"password": "scis2024", "role": "viewer",  "name": "业务查看员"},',
    '}\n\nROLE_PERMISSIONS = {',
    '    "admin":   ["home","import","forecast","inventory","replenish","transfer","logistics","guide","ops"],',
    '    "planner": ["home","import","forecast","inventory","replenish","transfer","logistics","guide"],',
    '    "viewer":  ["home","guide"],',
    '}\n\nROLE_ICONS = {"admin": "👑", "planner": "👤", "viewer": "🔍"}\n\n',
    'def get_user():',
    '    import streamlit as st',
    '    return st.session_state.get("user_info")\n\n',
    'def is_logged_in():',
    '    import streamlit as st',
    '    return st.session_state.get("user_logged_in", False) is True\n\n',
    'def get_allowed_pages():',
    '    user = get_user()',
    '    if not user: return []',
    '    role = user.get("role", "viewer")',
    '    allowed = set(ROLE_PERMISSIONS.get(role, []))',
    '    return [p for p in NAV_PAGES if p["key"] in allowed]',
    '"""',
    '',
    'if insert_after in content:',
    '    content = content.replace(insert_after, insert_after + user_config, 1)',
    '    print("OK: user_config")',
    'else:',
    '    print("FAIL: user_config")',
    '',
    '# 2. Logo区域后添加用户登录区',
    'old_logo = """SC-Decision Engine v1.0\n            </div>\n        </div>\n        \"\", unsafe_allow_html=True)\n        \n        # 初始化 session state"""',
    '',
    'new_logo = """SC-Decision Engine v1.0\n            </div>\n        </div>\n        \"\", unsafe_allow_html=True)\n        \n        # -- 用户登录区域 --\n        import streamlit as _st\n        _user = _st.session_state.get("user_info")\n        _logged_in = _st.session_state.get("user_logged_in", False)\n        if _logged_in and _user:\n            _role_icon = ROLE_ICONS.get(_user["role"], "👤")\n            _st.markdown(f\\'\\'\\'\\n            <div style="background: linear-gradient(135deg, #1B4965 0%, #457B9D 100%);\\n                        border-radius: 12px; padding: 16px; margin-bottom: 16px;\\n                        color: white; text-align: center;">\\n                <div style="font-size: 36px; margin-bottom: 8px;">{_role_icon}</div>\\n                <div style="font-weight: 600; font-size: 15px; margin-bottom: 2px;">{_user["name"]}</div>\\n                <div style="font-size: 12px; opacity: 0.85;">@{_user["role"]} | {_user["username"]}</div>\\n            </div>\\n            \\'\\'\\', unsafe_allow_html=True)\n            if _st.button("退出登录", use_container_width=True, key="sidebar_logout_btn"):\n                _st.session_state.user_logged_in = False\n                _st.session_state.user_info = None\n                _st.session_state.nav_page = None\n                _st.rerun()\n            _st.markdown("<div style=\\'height: 8px;\\'></div>", unsafe_allow_html=True)\n        else:\n            _st.markdown(\\'\\'\\'\\n            <div style="background: #F8FAFC; border-radius: 12px; padding: 16px; margin-bottom: 16px;\\n                        text-align: center; border: 1.5px dashed #CBD5E1;">\\n                <div style="font-size: 28px; margin-bottom: 8px;">🔒</div>\\n                <div style="font-weight: 600; color: #1B4965; font-size: 14px; margin-bottom: 4px;">未登录</div>\\n                <div style="font-size: 12px; color: #9CA3AF;">请登录以访问系统</div>\\n            </div>\\n            \\'\\'\\', unsafe_allow_html=True)\n            return None\n        \n        # 初始化 session state"""',
    '',
    'if old_logo in content:',
    '    content = content.replace(old_logo, new_logo, 1)',
    '    print("OK: user_area")',
    'else:',
    '    print("FAIL: user_area")',
    '',
    '# 3. 修改导航循环，添加权限过滤',
    'old_nav = """        # 渲染分组导航\n        for group in NAV_GROUPS:"""',
    'new_nav = """        # 获取当前用户可访问的页面\n        allowed_pages = get_allowed_pages()\n        allowed_keys = {p["key"] for p in allowed_pages}\n        \n        # 渲染分组导航（权限过滤）\n        for group in NAV_GROUPS:"""',
    '',
    'if old_nav in content:',
    '    content = content.replace(old_nav, new_nav, 1)',
    '    print("OK: nav_filter")',
    'else:',
    '    print("FAIL: nav_filter")',
    '',
    '# 4. 添加分组内页面过滤',
    'old_group = """            # 分组标题（居中 + 两侧装饰线）"""',
    'new_group = """            # 过滤该分组下允许的页面\n            group_pages = [pg for pg in group["pages"] if pg["key"] in allowed_keys]\n            if not group_pages:\n                continue\n            \n            # 分组标题（居中 + 两侧装饰线）"""',
    '',
    'if old_group in content:',
    '    content = content.replace(old_group, new_group, 1)',
    '    print("OK: group_filter")',
    'else:',
    '    print("FAIL: group_filter")',
    '',
    '# 5. 修改内层循环',
    'old_inner = """            for pg in group["pages"]:"""',
    'new_inner = """            for pg in group_pages:"""',
    '',
    'if old_inner in content:',
    '    content = content.replace(old_inner, new_inner, 1)',
    '    print("OK: inner_loop")',
    'else:',
    '    print("FAIL: inner_loop")',
    '',
    '# 6. 修改返回',
    'old_ret = """    return st.session_state.nav_page"""',
    'new_ret = """    if allowed_pages:\n        _current = st.session_state.get("nav_page")\n        _valid = {f"{p['icon']} {p['title']}" for p in allowed_pages}\n        if _current is None or _current not in _valid:\n            st.session_state.nav_page = f"{allowed_pages[0]['icon']} {allowed_pages[0]['title']}"\n        return st.session_state.nav_page\n    return None"""',
    '',
    'if old_ret in content:',
    '    content = content.replace(old_ret, new_ret, 1)',
    '    print("OK: return")',
    'else:',
    '    print("FAIL: return")',
    '',
    'with open("/opt/scis/components.py", "w", encoding="utf-8") as f:',
    '    f.write(content)',
    'print("DONE")',
    'PYEOF',
]

# 执行命令链
for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.close()

# 执行修复脚本
print("=== 执行修复脚本 ===")
stdin, stdout, stderr = client.exec_command('cd /opt/scis && python /tmp/fix_comp.py')
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')
print(out)
if err.strip():
    print("ERR:", err)

client.close()
print("\n修改完成")
