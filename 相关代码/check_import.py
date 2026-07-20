import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查第 30-45 行
stdin, stdout, stderr = client.exec_command('sed -n 30,50p /opt/scis/streamlit_app.py')
print(stdout.read().decode('utf-8'))

client.close()
