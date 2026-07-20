import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# === 修改1: components.py - 添加权限过滤 ===
stdin, stdout, stderr = client.exec_command('cat /opt/scis/components.py')
comp_content = stdout.read().decode('utf-8')

old_nav = '''        # 渲染分组导航
        for group in NAV_GROUPS:
            # 分组标题（居中 + 两侧装饰线）'''

new_nav = '''        # 权限过滤：获取用户允许的页面key
        allowed_keys = set(st.session_state.get("user_allowed_keys", []))
        
        # 渲染分组导航
        for group in NAV_GROUPS:
            # 过滤该分组下允许的页面
            group_pages = [pg for pg in group["pages"] if (not allowed_keys) or (pg["key"] in allowed_keys)]
            if not group_pages:
                continue
            
            # 分组标题（居中 + 两侧装饰线）'''

comp_content = comp_content.replace(old_nav, new_nav, 1)
print("OK: components.py nav filter")

# 修改内层循环
old_inner = '''            for pg in group["pages"]:'''
new_inner = '''            for pg in group_pages:'''
comp_content = comp_content.replace(old_inner, new_inner, 1)
print("OK: components.py inner loop")

# 写回 components.py
sftp = client.open_sftp()
with sftp.file('/opt/scis/components.py', 'w') as f:
    f.write(comp_content.encode('utf-8'))
print("OK: components.py written")

# === 修改2: streamlit_app.py - 登录时设置权限 ===
stdin, stdout, stderr = client.exec_command('cat /opt/scis/streamlit_app.py')
app_content = stdout.read().decode('utf-8')

old_login = '''                    st.session_state.user_logged_in = True
                    st.session_state.user_info = {"username": username, "name": USERS[username]["name"], "role": USERS[username]["role"]}
                    st.success(f"Welcome, {USERS[username]['name']}!")
                    st.rerun()'''

new_login = '''                    st.session_state.user_logged_in = True
                    st.session_state.user_info = {"username": username, "name": USERS[username]["name"], "role": USERS[username]["role"]}
                    st.session_state.user_allowed_keys = ROLE_PERMISSIONS[USERS[username]["role"]]
                    st.success(f"Welcome, {USERS[username]['name']}!")
                    st.rerun()'''

app_content = app_content.replace(old_login, new_login, 1)
print("OK: streamlit_app.py login role")

# 写回 streamlit_app.py
with sftp.file('/opt/scis/streamlit_app.py', 'w') as f:
    f.write(app_content.encode('utf-8'))
print("OK: streamlit_app.py written")

# 语法检查
stdin, stdout, stderr = client.exec_command('python3 -m py_compile /opt/scis/streamlit_app.py /opt/scis/components.py && echo "SYNTAX OK"')
out = stdout.read().decode('utf-8').strip()
err = stderr.read().decode('utf-8').strip()
print("语法:", out)
if err:
    print("ERR:", err)

client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
