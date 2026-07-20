import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 1. 从 git 恢复 components.py 到最新 commit 版本（即 Phase 5 完成时的版本）
stdin, stdout, stderr = client.exec_command('cd /opt/scis && git checkout HEAD -- components.py')
print("git checkout components.py:", stdout.read().decode('utf-8') or "OK", stderr.read().decode('utf-8') or "")

# 2. 也恢复 streamlit_app.py
stdin, stdout, stderr = client.exec_command('cd /opt/scis && git checkout HEAD -- streamlit_app.py')
print("git checkout streamlit_app.py:", stdout.read().decode('utf-8') or "OK", stderr.read().decode('utf-8') or "")

# 验证文件大小
stdin, stdout, stderr = client.exec_command('wc -c /opt/scis/components.py /opt/scis/streamlit_app.py')
print("文件大小:", stdout.read().decode('utf-8').strip())

client.close()
