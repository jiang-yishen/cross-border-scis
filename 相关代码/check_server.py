import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

stdin, stdout, stderr = client.exec_command('sed -n 443,452p /opt/scis/components.py')
print("=== Logo后区域 (443-452) ===")
print(repr(stdout.read().decode('utf-8')))

stdin, stdout, stderr = client.exec_command('sed -n 450,460p /opt/scis/components.py')
print("\n=== 导航区域 (450-460) ===")
print(repr(stdout.read().decode('utf-8')))

client.close()
