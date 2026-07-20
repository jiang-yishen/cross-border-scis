import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取文件
stdin, stdout, stderr = client.exec_command('cat /opt/scis/components.py')
content = stdout.read().decode('utf-8')

# 在 "初始化 session state" 前插入用户卡片
old = '        # 初始化 session state（保持与旧版radio返回格式一致）'

new = '''        # -- 用户信息卡片 + 退出 --
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
        
        # 初始化 session state（保持与旧版radio返回格式一致）'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: user card + logout added")
else:
    print("FAIL: not found")

# 写回
sftp = client.open_sftp()
with sftp.file('/opt/scis/components.py', 'w') as f:
    f.write(content.encode('utf-8'))
print("OK: file written")

# 语法检查
stdin, stdout, stderr = client.exec_command('python3 -m py_compile /opt/scis/components.py && echo "SYNTAX OK"')
print("语法:", stdout.read().decode('utf-8').strip())

client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
