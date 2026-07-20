import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 查找 Logo 区域和用户区域的代码
stdin, stdout, stderr = client.exec_command('grep -n "SC-Decision Engine v1.0" /opt/scis/components.py')
print("SC-Decision:", stdout.read().decode('utf-8').strip())

stdin, stdout, stderr = client.exec_command('grep -n "未登录" /opt/scis/components.py')
print("未登录:", stdout.read().decode('utf-8').strip())

stdin, stdout, stderr = client.exec_command('grep -n "用户登录区域" /opt/scis/components.py')
print("用户登录区域:", stdout.read().decode('utf-8').strip())

client.close()
