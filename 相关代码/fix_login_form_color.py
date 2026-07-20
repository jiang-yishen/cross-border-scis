import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

stdin, stdout, stderr = client.exec_command('cat /opt/scis/streamlit_app.py')
content = stdout.read().decode('utf-8')

# 查找登录表单区域的白色背景并替换为暖色调
# 常见模式：表单卡片、输入框区域、st.container 的样式
old_patterns = [
    # 模式1：表单区域白色背景（常见在 login form div）
    ('background:#FFFFFF;border-radius:20px;padding:40px;box-shadow:0 8px 32px rgba(0,0,0,0.1)',
     'background:#FFF8E7;border-radius:20px;padding:40px;box-shadow:0 8px 32px rgba(139,69,19,0.12);border:1px solid rgba(222,184,135,0.3)'),
    # 模式2：如果有白色卡片背景
    ('background:rgba(255,255,255,0.95)',
     'background:rgba(255,248,231,0.95)'),
    # 模式3：纯白色背景简写
    ('background:#fff',
     'background:#FFF8E7'),
    ('background:#FFF',
     'background:#FFF8E7'),
    # 模式4：登录标题区域
    ('<h2 style="text-align:center;margin-bottom:30px;color:#333;font-size:24px;font-weight:600;">系统登录',
     '<h2 style="text-align:center;margin-bottom:30px;color:#5D4037;font-size:24px;font-weight:600;">🐾 系统登录'),
    # 模式5：输入框标签颜色
    ('color:#666',
     'color:#8D6E63'),
    # 模式6：说明文字颜色
    ('color:#888',
     'color:#A1887F'),
]

changes = 0
for old, new in old_patterns:
    if old in content:
        content = content.replace(old, new, 1)
        changes += 1
        print(f"OK: replaced pattern {changes}")

if changes == 0:
    print("WARN: no direct patterns matched, trying fuzzy search...")
    # 尝试查找登录表单区域的关键词
    stdin, stdout, stderr = client.exec_command("grep -n '系统登录' /opt/scis/streamlit_app.py | head -5")
    print("grep 结果:", stdout.read().decode('utf-8').strip())

# 写回
sftp = client.open_sftp()
with sftp.file('/opt/scis/streamlit_app.py', 'w') as f:
    f.write(content.encode('utf-8'))
print(f"OK: file written ({changes} changes)")

# 语法检查
stdin, stdout, stderr = client.exec_command('python3 -m py_compile /opt/scis/streamlit_app.py && echo "SYNTAX OK"')
print("语法:", stdout.read().decode('utf-8').strip())
err = stderr.read().decode('utf-8').strip()
if err:
    print("错误:", err)

client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")
client.close()
