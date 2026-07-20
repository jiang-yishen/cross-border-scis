import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取 components.py
stdin, stdout, stderr = client.exec_command('cat /opt/scis/components.py')
content = stdout.read().decode('utf-8')

# 在 Logo 区域后添加用户卡片和退出按钮
old_logo = '        <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 10px 0;">\n        """, unsafe_allow_html=True)\n\n        # 初始化 session state'

new_user_card = '''        <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 10px 0;">
        """, unsafe_allow_html=True)

        # -- 用户信息 + 退出 --
        user_info = st.session_state.get("user_info")
        if user_info:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1B4965 0%, #457B9D 100%);
                        border-radius: 10px; padding: 12px; margin: 8px 0;
                        color: white; text-align: center;">
                <div style="font-size: 22px; margin-bottom: 4px;">👤</div>
                <div style="font-weight: 600; font-size: 14px;">{user_info["name"]}</div>
                <div style="font-size: 11px; opacity: 0.85;">{user_info["role"]}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚪 退出", use_container_width=True, key="sidebar_logout_btn"):
                st.session_state.user_logged_in = False
                st.session_state.user_info = None
                st.session_state.user_allowed_keys = []
                st.session_state.nav_page = None
                st.rerun()
        
        # 初始化 session状态'''

if old_logo in content:
    content = content.replace(old_logo, new_user_card, 1)
    print("OK: user card added")
else:
    print("FAIL: logo area not found")

# 写回
sftp = client.open_sftp()
with sftp.file('/opt/scis/components.py', 'w') as f:
    f.write(content.encode('utf-8'))
print("OK: file written")

# 语法检查
stdin, stdout, stderr = client.exec_command('python3 -m py_compile /opt/scis/components.py && echo "SYNTAX OK"')
out = stdout.read().decode('utf-8').strip()
print("语法:", out)

client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
