import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取实际代码
stdin, stdout, stderr = client.exec_command('sed -n 413,445p /opt/scis/components.py')
print("=== 413-445 ===")
print(stdout.read().decode('utf-8'))

client.close()
