import paramiko
import base64

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

stdin, stdout, stderr = client.exec_command('cat /opt/scis/components.py')
content = stdout.read().decode('utf-8')

# 问题：_st 可能和 st 不是同一个 session_state 引用
# 修复：将 _st 改为直接使用 st（因为文件开头已经 import streamlit as st）

old_code = '''        # -- 用户登录区域 --
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
            return None'''

new_code = '''        # -- 用户登录区域 --
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
            return None'''

if old_code in content:
    content = content.replace(old_code, new_code, 1)
    print("✅ 用户登录区域修复成功")
else:
    print("❌ 未找到匹配")

encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /opt/scis/components.py')
err = stderr.read().decode('utf-8')
if err.strip():
    print("ERR:", err)
else:
    print("✅ 文件已写入")

client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
