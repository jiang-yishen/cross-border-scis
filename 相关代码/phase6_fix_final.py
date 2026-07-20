import paramiko
import base64

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取文件
stdin, stdout, stderr = client.exec_command('cat /opt/scis/components.py')
content = stdout.read().decode('utf-8')

# 修复1: Logo后添加用户区域
old1 = '''        """, unsafe_allow_html=True)

        

        # 初始化 session state（保持与旧版radio返回格式一致）'''

new1 = '''        """, unsafe_allow_html=True)

        

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
    print("❌ 1. 未找到")

# 修复2: 导航循环添加权限过滤
old2 = '''        

        # 渲染分组导航

        for group in NAV_GROUPS:

            # 分组标题（居中 + 两侧装饰线）'''

new2 = '''        

        # 获取当前用户可访问的页面
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
    print("❌ 2. 未找到")

# 写回文件（base64编码避免SSH问题）
encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /opt/scis/components.py')
err = stderr.read().decode('utf-8')
if err.strip():
    print("ERR:", err)
else:
    print("✅ 文件已写入")

client.close()
print("\n🎉 修改完成！")
