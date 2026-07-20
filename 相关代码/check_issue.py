import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取关键区域
stdin, stdout, stderr = client.exec_command('sed -n 693,710p /opt/scis/components.py')
print("=== 693-710 ===")
print(stdout.read().decode('utf-8'))

# 查找所有 def sidebar_navigation 的位置
stdin, stdout, stderr = client.exec_command('grep -n "def sidebar_navigation" /opt/scis/components.py')
print("\n=== 所有 sidebar_navigation 定义 ===")
print(stdout.read().decode('utf-8'))

client.close()
