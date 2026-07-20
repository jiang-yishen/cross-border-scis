import paramiko

# 读取本地备份
with open('components_backup_phase6.py', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"原始文件: {len(content)} 字符, {content.count(chr(10))} 行")

# 修复: 替换所有 \r\r\n 为 \r\n (Read 工具显示的问题)
content = content.replace('\r\r\n', '\r\n')

# 1. 修改 Logo 区域后添加用户登录区
old1 = '''        "", unsafe_allow_html=True)
        
        # 初始化 session state（保持与旧版radio返回格式一致）'''

new1 = '''        "", unsafe_allow_html=True)
        
        # -- 用户登录区域 --
        import streamlit as _st
        _user = _st.session_state.get("user_info")
        _logged_in = _st.session_state.get("user_logged_in", False)
        if _logged_in and _user:
            _role_icon = ROLE_ICONS.get(_user["role"], "👤")
            _st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1B4965 0%, #457B9D 100%);
                        border-radius: 12px; padding: 16px; margin-bottom: 16px;
                        color: white; text-align: center;">
                <div style="font-size: 36px; margin-bottom: 8px;">{_role_icon}</div>
                <div style="font-weight: 600; font-size: 15px; margin-bottom: 2px;">{_user["name"]}</div>
                <div style="font-size: 12px; opacity: 0.85;">@{_user["role"]} | {_user["username"]}</div>
            </div>
            """, unsafe_allow_html=True)
            if _st.button("🚪 退出登录", use_container_width=True, key="sidebar_logout_btn"):
                _st.session_state.user_logged_in = False
                _st.session_state.user_info = None
                _st.session_state.nav_page = None
                _st.rerun()
            _st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        else:
            _st.markdown("""
            <div style="background: #F8FAFC; border-radius: 12px; padding: 16px; margin-bottom: 16px;
                        text-align: center; border: 1.5px dashed #CBD5E1;">
                <div style="font-size: 28px; margin-bottom: 8px;">🔒</div>
                <div style="font-weight: 600; color: #1B4965; font-size: 14px; margin-bottom: 4px;">未登录</div>
                <div style="font-size: 12px; color: #9CA3AF;">请登录以访问系统</div>
            </div>
            """, unsafe_allow_html=True)
            return None
        
        # 初始化 session state（保持与旧版radio返回格式一致）'''

if old1 in content:
    content = content.replace(old1, new1, 1)
    print("✅ 1. 用户登录区域")
else:
    print("❌ 1. 未找到匹配")

# 2. 修改导航循环 - 添加权限过滤
old2 = '''        # 渲染分组导航
        for group in NAV_GROUPS:
            # 分组标题（居中 + 两侧装饰线）'''

new2 = '''        # 获取当前用户可访问的页面
        allowed_pages = get_allowed_pages()
        allowed_keys = {p["key"] for p in allowed_pages}
        
        # 渲染分组导航（权限过滤）
        for group in NAV_GROUPS:
            # 过滤该分组下允许的页面
            group_pages = [pg for pg in group["pages"] if pg["key"] in allowed_keys]
            if not group_pages:
                continue
            
            # 分组标题（居中 + 两侧装饰线）'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("✅ 2. 导航权限过滤")
else:
    print("❌ 2. 未找到匹配")

# 3. 修改内层循环
old3 = '''            for pg in group["pages"]:'''
new3 = '''            for pg in group_pages:'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print("✅ 3. 内层循环")
else:
    print("❌ 3. 未找到匹配")

# 4. 修改返回
old4 = '''        return st.session_state.nav_page'''
new4 = '''        if allowed_pages:
            _current = st.session_state.get("nav_page")
            _valid = {f"{p['icon']} {p['title']}" for p in allowed_pages}
            if _current is None or _current not in _valid:
                st.session_state.nav_page = f"{allowed_pages[0]['icon']} {allowed_pages[0]['title']}"
            return st.session_state.nav_page
        return None'''

if old4 in content:
    content = content.replace(old4, new4, 1)
    print("✅ 4. 返回语句")
else:
    print("❌ 4. 未找到匹配")

# 保存到本地
with open('components_new.py', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n✅ 新文件已保存: {len(content)} 字符")

# 上传到服务器
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

sftp = client.open_sftp()
sftp.put('components_new.py', '/opt/scis/components.py')
print("✅ 已上传到服务器 /opt/scis/components.py")

sftp.close()
client.close()
print("\n🎉 Phase 6 components.py 修改完成！")
