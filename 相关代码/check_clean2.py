import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取关键区域
stdin, stdout, stderr = client.exec_command('sed -n 320,375p /opt/scis/components.py')
print("=== 320-375 ===")
print(stdout.read().decode('utf-8'))

stdin, stdout, stderr = client.exec_command('sed -n 340,365p /opt/scis/components.py')
print("\n=== 340-365 ===")
print(repr(stdout.read().decode('utf-8')))

client.close()
