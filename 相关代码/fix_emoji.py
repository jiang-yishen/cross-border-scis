import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

stdin, stdout, stderr = client.exec_command('cat /opt/scis/streamlit_app.py')
content = stdout.read().decode('utf-8')

# 把所有 🐱 替换为 🐈（全身猫，各平台渲染更一致）
content = content.replace('🐱', '🐈')
print('OK: replaced cat emoji')

sftp = client.open_sftp()
with sftp.file('/opt/scis/streamlit_app.py', 'w') as f:
    f.write(content.encode('utf-8'))
print('OK: written')

stdin, stdout, stderr = client.exec_command('python3 -m py_compile /opt/scis/streamlit_app.py && echo "SYNTAX OK"')
print('语法:', stdout.read().decode('utf-8').strip())

client.exec_command('sudo systemctl restart scis-streamlit')
print('🔄 服务已重启')
client.close()
