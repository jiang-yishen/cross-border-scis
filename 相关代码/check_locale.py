import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查服务器 locale 和 Python 编码
stdin, stdout, stderr = client.exec_command('locale')
print("=== locale ===")
print(stdout.read().decode('utf-8'))

stdin, stdout, stderr = client.exec_command('python3 -c "import sys; print(sys.getdefaultencoding(), sys.stdout.encoding)"')
print("=== Python encoding ===")
print(stdout.read().decode('utf-8'))

# 检查 Streamlit 版本
stdin, stdout, stderr = client.exec_command('/opt/scis/venv/bin/python -c "import sys; print(sys.getdefaultencoding(), sys.stdout.encoding)"')
print("=== Streamlit venv encoding ===")
print(stdout.read().decode('utf-8'))

# 检查系统 locale
stdin, stdout, stderr = client.exec_command('echo $LANG $LC_ALL')
print("=== ENV locale ===")
print(stdout.read().decode('utf-8'))

client.close()
