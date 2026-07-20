import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取导航循环区域
stdin, stdout, stderr = client.exec_command('sed -n 408,450p /opt/scis/components.py')
print("=== 导航循环 (408-450) ===")
print(stdout.read().decode('utf-8'))

client.close()
