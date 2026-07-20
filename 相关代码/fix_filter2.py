import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取完整文件
stdin, stdout, stderr = client.exec_command('cat /opt/scis/components.py')
content = stdout.read().decode('utf-8')

# 使用 \r\n 换行符匹配
old = '        # 渲染分组导航\r\n        for group in NAV_GROUPS:\r\n            # 分组标题（居中 + 两侧装饰线）'

new = '''        # 权限过滤\r\n        allowed_keys = set(st.session_state.get("user_allowed_keys", []))\r\n        \r\n        # 渲染分组导航\r\n        for group in NAV_GROUPS:\r\n            # 过滤该分组下允许的页面\r\n            group_pages = [pg for pg in group["pages"] if (not allowed_keys) or (pg["key"] in allowed_keys)]\r\n            if not group_pages:\r\n                continue\r\n            \r\n            # 分组标题（居中 + 两侧装饰线）'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: filter inserted")
else:
    print("FAIL: still not found")

# 写回
sftp = client.open_sftp()
with sftp.file('/opt/scis/components.py', 'w') as f:
    f.write(content.encode('utf-8'))
print("OK: file written")

client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
