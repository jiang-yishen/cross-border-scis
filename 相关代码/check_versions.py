import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查 phase0 备份的大小
stdin, stdout, stderr = client.exec_command('wc -c /opt/scis/streamlit_app.py.backup.phase0 /opt/scis/streamlit_app.py')
print("文件大小对比:")
print(stdout.read().decode('utf-8'))

# 检查 GitHub 上的最新版本
stdin, stdout, stderr = client.exec_command('curl -sI https://raw.githubusercontent.com/jiang-yishen/cross-border-scis/main/streamlit_app.py | grep -i content-length')
print("\nGitHub 文件大小:")
print(stdout.read().decode('utf-8'))

client.close()
