import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 1. 恢复 streamlit_app.py
client.exec_command('cd /opt/scis && git checkout HEAD -- streamlit_app.py')
print("git restored")

# 2. 检查完整的 from components import 语句
stdin, stdout, stderr = client.exec_command("grep -n -A 20 'from components import' /opt/scis/streamlit_app.py | head -25")
print("import block:")
print(stdout.read().decode('utf-8'))

client.close()
