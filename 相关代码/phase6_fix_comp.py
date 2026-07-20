import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 在服务器上执行 Python 脚本修改 components.py
modify_script = '''
import re

# 读取文件
with open("/opt/scis/components.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. 在 NAV_PAGES 定义后、函数定义前添加用户配置
insert_after = """NAV_PAGES = []
for g in NAV_GROUPS:
    NAV_PAGES.extend(g["pages"])"""

user_config = """

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
    return __import__("streamlit").session_state.get("user_info")

def is_logged_in():
    return __import__("streamlit").session_state.get("user_logged_in", False) is True

def get_allowed_pages():
    user = get_user()
    if not user:
        return []
    role = user.get("role", "viewer")
    allowed_keys = set(ROLE_PERMISSIONS.get(role, []))
    return [p for p in NAV_PAGES if p["key"] in allowed_keys]

"""

if insert_after in content:
    content = content.replace(insert_after, insert_after + user_config, 1)
    print("✅ 用户配置添加成功")
else:
    print("❌ NAV_PAGES 定义未找到")

# 2. 修改 sidebar_navigation 函数，添加用户区域 + 权限过滤
# 在函数开头（st.markdown 注入CSS之后）添加用户区域
old_logo = '''        st.markdown("""
        <div style="text-align: center; padding: 20px 12px 16px 12px; 
                    background: linear-gradient(135deg, #1B4965 0%, #234B6B 100%);
                    border-radius: 12px; margin: 0 0 14px 0;
                    box-shadow: 0 2px 8px rgba(27,73,101,0.2);">
            <div style="font-size: 36px; margin-bottom: 8px;">🌐</div>
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; line-height: 1.4;">
                跨境海外仓<br>供应链智能决策系统
            </div>
            <div style="display: inline-block; background: rgba(255,255,255,0.15); 
                        color: #FFFFFF; font-size: 9px; font-weight: 600; 
                        padding: 3px 12px; border-radius: 20px; margin-top: 10px;">
                SC-Decision Engine v1.0
            </div>
        </div>
        """, unsafe_allow_html=True)'''

new_logo_user = '''        st.markdown("""
        <div style="text-align: center; padding: 20px 12px 16px 12px; 
                    background: linear-gradient(135deg, #1B4965 0%, #234B6B 100%);
                    border-radius: 12px; margin: 0 0 14px 0;
                    box-shadow: 0 2px 8px rgba(27,73,101,0.2);">
            <div style="font-size: 36px; margin-bottom: 8px;">🌐</div>
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; line-height: 1.4;">
                跨境海外仓<br>供应链智能决策系统
            </div>
            <div style="display: inline-block; background: rgba(255,255,255,0.15); 
                        color: #FFFFFF; font-size: 9px; font-weight: 600; 
                        padding: 3px 12px; border-radius: 20px; margin-top: 10px;">
                SC-Decision Engine v1.0
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ── 用户登录区域 ──
        import streamlit as st_local
        user = st_local.session_state.get("user_info")
        logged_in = st_local.session_state.get("user_logged_in", False)
        if logged_in and user:
            role_icon = ROLE_ICONS.get(user["role"], "👤")
            st_local.markdown(f"""
            <div style="background: linear-gradient(135deg, #1B4965 0%, #457B9D 100%);
                        border-radius: 12px; padding: 16px; margin-bottom: 16px;
                        color: white; text-align: center;">
                <div style="font-size: 36px; margin-bottom: 8px;">{role_icon}</div>
                <div style="font-weight: 600; font-size: 15px; margin-bottom: 2px;">{user["name"]}</div>
                <div style="font-size: 12px; opacity: 0.85;">@{user["role"]} | {user["username"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st_local.button("🚪 退出登录", use_container_width=True, key="sidebar_logout_btn"):
                st_local.session_state.user_logged_in = False
                st_local.session_state.user_info = None
                st_local.session_state.nav_page = None
                st_local.rerun()
            st_local.markdown("<div style=\'height: 8px;\'></div>", unsafe_allow_html=True)
        else:
            st_local.markdown("""
            <div style="background: #F8FAFC; border-radius: 12px; padding: 16px; margin-bottom: 16px;
                        text-align: center; border: 1.5px dashed #CBD5E1;">
                <div style="font-size: 28px; margin-bottom: 8px;">🔒</div>
                <div style="font-weight: 600; color: #1B4965; font-size: 14px; margin-bottom: 4px;">未登录</div>
                <div style="font-size: 12px; color: #9CA3AF;">请登录以访问系统</div>
            </div>
            """, unsafe_allow_html=True)
            return None'''

if old_logo in content:
    content = content.replace(old_logo, new_logo_user, 1)
    print("✅ 用户区域添加成功")
else:
    print("❌ Logo区域未找到")

# 3. 修改导航循环，添加权限过滤
old_nav_loop = '''        # 渲染分组导航
        for group in NAV_GROUPS:
            # 分组标题（居中 + 两侧装饰线）'''

new_nav_loop = '''        # 获取当前用户可访问的页面
        allowed_pages = get_allowed_pages()
        allowed_keys = {p["key"] for p in allowed_pages}
        
        # 渲染分组导航（过滤权限）
        for group in NAV_GROUPS:
            # 过滤该分组下允许的页面
            group_pages = [pg for pg in group["pages"] if pg["key"] in allowed_keys]
            if not group_pages:
                continue
            
            # 分组标题（居中 + 两侧装饰线）'''

if old_nav_loop in content:
    content = content.replace(old_nav_loop, new_nav_loop, 1)
    print("✅ 导航权限过滤添加成功")
else:
    print("❌ 导航循环未找到")

# 4. 修改内部循环变量名 pg -> group_pages
old_for_pg = '''            for pg in group["pages"]:'''
new_for_pg = '''            for pg in group_pages:'''

if old_for_pg in content:
    content = content.replace(old_for_pg, new_for_pg, 1)
    print("✅ 内部循环变量更新成功")
else:
    print("❌ 内部循环未找到")

# 5. 修改返回语句
old_return = '''    return st.session_state.nav_page'''
new_return = '''    if allowed_pages:
        current = st.session_state.get("nav_page")
        if current and current not in {f"{p['icon']} {p['title']}" for p in allowed_pages}:
            st.session_state.nav_page = f"{allowed_pages[0]['icon']} {allowed_pages[0]['title']}"
        return st.session_state.nav_page
    return None'''

if old_return in content:
    content = content.replace(old_return, new_return, 1)
    print("✅ 返回语句更新成功")
else:
    print("❌ 返回语句未找到")

# 写回文件
with open("/opt/scis/components.py", "w", encoding="utf-8") as f:
    f.write(content)
print("\\n✅ components.py 保存成功")
'''

# 在服务器上写入临时脚本并执行
sftp = client.open_sftp()
with sftp.file('/tmp/fix_components.py', 'w') as f:
    f.write(modify_script.encode('utf-8'))

stdin, stdout, stderr = client.exec_command('cd /opt/scis && python /tmp/fix_components.py')
print("=== 输出 ===")
print(stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("=== 错误 ===")
    print(err)

client.close()
print("\n🎉 修改完成！")
