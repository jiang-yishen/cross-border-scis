import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查 with st.sidebar 块中的代码结构
stdin, stdout, stderr = client.exec_command('sed -n 840,900p /opt/scis/components.py')
print(stdout.read().decode('utf-8'))

client.close()
