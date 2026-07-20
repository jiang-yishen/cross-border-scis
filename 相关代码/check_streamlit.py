import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查导入语句
stdin, stdout, stderr = client.exec_command('grep -n "from components import" /opt/scis/streamlit_app.py')
print("导入:", stdout.read().decode('utf-8').strip())

# 检查 main() 开头
stdin, stdout, stderr = client.exec_command('sed -n 2310,2335p /opt/scis/streamlit_app.py')
print("\nmain():", repr(stdout.read().decode('utf-8')))

client.close()
