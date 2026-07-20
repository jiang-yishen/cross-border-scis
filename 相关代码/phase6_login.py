import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# ============================================
# 修改1: components.py - sidebar_navigation() 添加用户区域+权限过滤
# ============================================
print("=== 修改 components.py ===")

sftp = client.open_sftp()
with sftp.file('/opt/scis/components.py', 'r') as f:
    comp_content = f.read().decode('utf-8')

# 在 sidebar_navigation() 函数开头，注入用户区域 + 权限过滤逻辑
old_sidebar_start = '''def sidebar_navigation():
    """渲染侧边栏大卡片导航，返回用户选择的页面标题字符串"""
    # 注入导航卡片CSS（加宽侧边栏 + 美化按钮为大卡片）'''

new_sidebar_start = '''# 用户权限配置（预置账户）
USERS = {
    "admin": {"password": "jwyjys5210", "role": "admin", "name": "系统管理员"},
    "planner": {"password": "scis2024", "role": "planner", "name": "计划主管"},
    "viewer": {"password": "scis2024", "role": "viewer", "name": "业务查看员"},
}

# 权限映射：role -> 可访问的页面key列表
ROLE_PERMISSIONS = {
    "admin": ["home", "import", "forecast", "inventory", "replenish", "transfer", "logistics", "guide", "ops"],
    "planner": ["home", "import", "forecast", "inventory", "replenish", "transfer", "logistics", "guide"],
    "viewer": ["home", "guide"],
}

# 图标映射
ROLE_ICONS = {"admin": "👑", "planner": "👤", "viewer": "🔍"}

def get_user():
    """获取当前登录用户信息"""
    return st.session_state.get("user_info")

def is_logged_in():
    """检查是否已登录"""
    return st.session_state.get("user_logged_in", False) is True

def get_allowed_pages():
    """获取当前用户可访问的页面列表"""
    user = get_user()
    if not user:
        return []
    role = user.get("role", "viewer")
    allowed_keys = ROLE_PERMISSIONS.get(role, [])
    return [p for p in NAV_PAGES if p["key"] in allowed_keys]

def sidebar_navigation():
    """渲染侧边栏大卡片导航，返回用户选择的页面标题字符串"""
    
    # ── 用户登录区域（侧边栏顶部） ──
    user = get_user()
    if is_logged_in() and user:
        # 已登录：显示用户卡片 + 退出按钮
        role_icon = ROLE_ICONS.get(user["role"], "👤")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1B4965 0%, #457B9D 100%);
                    border-radius: 12px; padding: 16px; margin-bottom: 16px;
                    color: white; text-align: center;">
            <div style="font-size: 36px; margin-bottom: 8px;">{role_icon}</div>
            <div style="font-weight: 600; font-size: 15px; margin-bottom: 2px;">{user["name"]}</div>
            <div style="font-size: 12px; opacity: 0.85;">@{user["role"]} | {user["username"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 退出登录", use_container_width=True, key="sidebar_logout_btn"):
            st.session_state.user_logged_in = False
            st.session_state.user_info = None
            st.session_state.selected_page = None
            st.rerun()
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    else:
        # 未登录：显示提示
        st.markdown("""
        <div style="background: #F8FAFC; border-radius: 12px; padding: 16px; margin-bottom: 16px;
                    text-align: center; border: 1.5px dashed #CBD5E1;">
            <div style="font-size: 28px; margin-bottom: 8px;">🔒</div>
            <div style="font-weight: 600; color: #1B4965; font-size: 14px; margin-bottom: 4px;">未登录</div>
            <div style="font-size: 12px; color: #9CA3AF;">请登录以访问系统</div>
        </div>
        """, unsafe_allow_html=True)
        return None  # 未登录不显示导航
    
    # 注入导航卡片CSS（加宽侧边栏 + 美化按钮为大卡片）'''

if old_sidebar_start in comp_content:
    comp_content = comp_content.replace(old_sidebar_start, new_sidebar_start, 1)
    print("✅ sidebar_navigation() 用户区域添加成功")
else:
    print("❌ sidebar_navigation() 未找到")

# 修改导航按钮渲染逻辑，根据权限过滤
old_nav_logic = '''    for group in NAV_GROUPS:
        # 分组标题
        st.markdown(f"""
        <div style="font-size: 13px; font-weight: 700; color: #94A3B8;
                    margin: 20px 0 10px 0; padding: 0 8px;
                    letter-spacing: 1px; text-align: center;">
            {group["title"]}
        </div>
        """, unsafe_allow_html=True)
        
        for page in group["pages"]:
            is_selected = (st.session_state.get("selected_page") == page["title"])
            
            icon = page["icon"]
            title = page["title"]
            desc = page.get("desc", "")
            color = page.get("color", "#1B4965")
            
            # 根据选中状态设置样式
            if is_selected:
                bg = "#E8F4F8"
                border_color = color
                left_bar = color
                icon_opacity = "1"
                text_weight = "700"
            else:
                bg = "#FFFFFF"
                border_color = "#E2E8F0"
                left_bar = "transparent"
                icon_opacity = "0.7"
                text_weight = "500"
            
            btn_container = st.container()
            with btn_container:
                # 使用 HTML 渲染卡片外壳
                st.markdown(f"""
                <div style="background: {bg}; border-radius: 10px; border: 1.5px solid {border_color};
                            border-left: 4px solid {left_bar};
                            padding: 12px 14px; margin-bottom: 6px; cursor: pointer;
                            transition: all 0.2s ease;"
                            onmouseover="this.style.background='#F8FAFC'"
                            onmouseout="this.style.background='{bg}'">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 20px; opacity: {icon_opacity};">{icon}</span>
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-weight: {text_weight}; color: #1E293B; font-size: 14px; line-height: 1.2;">
                                {title}
                            </div>
                            <div style="font-size: 11px; color: #94A3B8; margin-top: 2px; line-height: 1.2;">
                                {desc}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 在卡片区域叠加透明按钮
                clicked = st.button(
                    f"{icon} {title}",
                    key=f"nav_{page['key']}",
                    use_container_width=True,
                    type="secondary" if not is_selected else "primary"
                )
                if clicked:
                    st.session_state.selected_page = page["title"]
                    st.rerun()
    
    # 返回当前选中的页面
    return st.session_state.get("selected_page", NAV_PAGES[0]["title"])'''

new_nav_logic = '''    # 获取当前用户可访问的页面
    allowed_pages = get_allowed_pages()
    allowed_keys = {p["key"] for p in allowed_pages}
    
    # 构建过滤后的分组
    for group in NAV_GROUPS:
        # 过滤该分组下允许的页面
        group_pages = [p for p in group["pages"] if p["key"] in allowed_keys]
        if not group_pages:
            continue  # 该分组无权限页面，跳过
        
        # 分组标题
        st.markdown(f"""
        <div style="font-size: 13px; font-weight: 700; color: #94A3B8;
                    margin: 20px 0 10px 0; padding: 0 8px;
                    letter-spacing: 1px; text-align: center;">
            {group["title"]}
        </div>
        """, unsafe_allow_html=True)
        
        for page in group_pages:
            is_selected = (st.session_state.get("selected_page") == page["title"])
            
            icon = page["icon"]
            title = page["title"]
            desc = page.get("desc", "")
            color = page.get("color", "#1B4965")
            
            # 根据选中状态设置样式
            if is_selected:
                bg = "#E8F4F8"
                border_color = color
                left_bar = color
                icon_opacity = "1"
                text_weight = "700"
            else:
                bg = "#FFFFFF"
                border_color = "#E2E8F0"
                left_bar = "transparent"
                icon_opacity = "0.7"
                text_weight = "500"
            
            btn_container = st.container()
            with btn_container:
                # 使用 HTML 渲染卡片外壳
                st.markdown(f"""
                <div style="background: {bg}; border-radius: 10px; border: 1.5px solid {border_color};
                            border-left: 4px solid {left_bar};
                            padding: 12px 14px; margin-bottom: 6px; cursor: pointer;
                            transition: all 0.2s ease;"
                            onmouseover="this.style.background='#F8FAFC'"
                            onmouseout="this.style.background='{bg}'">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 20px; opacity: {icon_opacity};">{icon}</span>
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-weight: {text_weight}; color: #1E293B; font-size: 14px; line-height: 1.2;">
                                {title}
                            </div>
                            <div style="font-size: 11px; color: #94A3B8; margin-top: 2px; line-height: 1.2;">
                                {desc}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 在卡片区域叠加透明按钮
                clicked = st.button(
                    f"{icon} {title}",
                    key=f"nav_{page['key']}",
                    use_container_width=True,
                    type="secondary" if not is_selected else "primary"
                )
                if clicked:
                    st.session_state.selected_page = page["title"]
                    st.rerun()
    
    # 返回当前选中的页面
    if allowed_pages:
        current = st.session_state.get("selected_page")
        if current not in {p["title"] for p in allowed_pages}:
            st.session_state.selected_page = allowed_pages[0]["title"]
        return st.session_state.get("selected_page", allowed_pages[0]["title"])
    return None'''

if old_nav_logic in comp_content:
    comp_content = comp_content.replace(old_nav_logic, new_nav_logic, 1)
    print("✅ 导航权限过滤逻辑添加成功")
else:
    print("❌ 导航按钮渲染逻辑未找到")

with sftp.file('/opt/scis/components.py', 'w') as f:
    f.write(comp_content.encode('utf-8'))
print("✅ components.py 已写入服务器")

# ============================================
# 修改2: streamlit_app.py - 添加 page_login() + 修改 main()
# ============================================
print("\n=== 修改 streamlit_app.py ===")

with sftp.file('/opt/scis/streamlit_app.py', 'r') as f:
    app_content = f.read().decode('utf-8')

# 2a. 在 main() 之前添加 page_login() 函数
login_func = '''

# =============================================================================
# 登录页面
# =============================================================================

def page_login():
    """用户登录页面"""
    # 左侧装饰区域
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
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 14px; line-height: 1.6;">
                从需求预测到库存优化<br>全链路智能决策平台
            </p>
            <div style="margin-top: 32px; display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 700;">1,100+</div>
                    <div style="font-size: 12px; opacity: 0.7;">SKU覆盖</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 700;">6</div>
                    <div style="font-size: 12px; opacity: 0.7;">海外仓库</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 700;">2026</div>
                    <div style="font-size: 12px; opacity: 0.7;">系统版本</div>
                </div>
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
            username = st.text_input("用户名", placeholder="请输入用户名", key="login_username")
            password = st.text_input("密码", type="password", placeholder="请输入密码", key="login_password")
            
            col_btn, col_hint = st.columns([1, 1])
            with col_btn:
                submitted = st.form_submit_button("🚀 登录", use_container_width=True, type="primary")
            
            if submitted:
                from components import USERS
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
                    st.error("❌ 用户名或密码错误，请重试")
        
        # 试玩账号提示
        st.markdown("""
        <div style="background: #F8FAFC; border-radius: 10px; padding: 16px; margin-top: 16px;
                    border: 1px dashed #CBD5E1;">
            <p style="color: #1B4965; font-weight: 600; margin: 0 0 8px 0; font-size: 13px;">🎮 试玩账号</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; color: #4B5563;">
                <div><b>admin</b> / jwyjys5210</div>
                <div><span style="color: #9CA3AF;">管理员·全权限</span></div>
                <div><b>planner</b> / scis2024</div>
                <div><span style="color: #9CA3AF;">计划员·运营模块</span></div>
                <div><b>viewer</b> / scis2024</div>
                <div><span style="color: #9CA3AF;">查看员·只读权限</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

'''

# 找到插入位置（在 main() 函数之前）
insert_marker = "# =============================================================================\n# 主入口\n# ============================================================================="
if insert_marker in app_content:
    app_content = app_content.replace(insert_marker, login_func + insert_marker, 1)
    print("✅ page_login() 函数添加成功")
else:
    print("❌ 插入位置未找到")

# 2b. 修改 main() 函数，添加登录状态检查
old_main = '''def main():
    """主入口：初始化 + 页面路由"""
    # 全局配置
    set_page_config()
    apply_custom_css()
    
    # 侧边栏导航
    selected_page = sidebar_navigation()
    
    # 页面路由
    if selected_page == "🏠 首页仪表盘":'''

new_main = '''def main():
    """主入口：初始化 + 页面路由"""
    # 全局配置
    set_page_config()
    apply_custom_css()
    
    # ── 登录状态初始化 ──
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    
    # 侧边栏导航（未登录返回 None）
    selected_page = sidebar_navigation()
    
    # ── 未登录 → 显示登录页 ──
    if not st.session_state.get("user_logged_in", False):
        page_login()
        return
    
    # ── 已登录 → 页面路由 ──
    if selected_page == "🏠 首页仪表盘":'''

if old_main in app_content:
    app_content = app_content.replace(old_main, new_main, 1)
    print("✅ main() 登录路由逻辑添加成功")
else:
    print("❌ main() 未找到")

with sftp.file('/opt/scis/streamlit_app.py', 'w') as f:
    f.write(app_content.encode('utf-8'))
print("✅ streamlit_app.py 已写入服务器")

sftp.close()
client.close()
print("\n🎉 Phase 6 登录验证系统修改完成！")
