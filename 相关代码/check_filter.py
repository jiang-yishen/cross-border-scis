import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取 408-415 行
stdin, stdout, stderr = client.exec_command('sed -n 408,415p /opt/scis/components.py')
print("=== 408-415 ===")
print(stdout.read().decode('utf-8'))

client.close()
