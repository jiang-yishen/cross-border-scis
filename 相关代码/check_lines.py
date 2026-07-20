import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 找到关键行号
stdin, stdout, stderr = client.exec_command('grep -n "SC-Decision Engine v1.0" /opt/scis/components.py')
print("SC-Decision:", stdout.read().decode('utf-8').strip())

stdin, stdout, stderr = client.exec_command('grep -n "初始化 session state" /opt/scis/components.py')
print("session state:", stdout.read().decode('utf-8').strip())

stdin, stdout, stderr = client.exec_command('grep -n "渲染分组导航" /opt/scis/components.py')
print("渲染分组:", stdout.read().decode('utf-8').strip())

client.close()
