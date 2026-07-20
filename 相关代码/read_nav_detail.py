import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取完整的 sidebar_navigation() 函数（从 def 到函数结束）
stdin, stdout, stderr = client.exec_command('grep -n "def sidebar_navigation" /opt/scis/components.py')
print("sidebar_navigation 行号:", stdout.read().decode('utf-8').strip())

# 读取函数定义行
stdin, stdout, stderr = client.exec_command('grep -n "def sidebar_navigation" /opt/scis/components.py')
line_num = int(stdout.read().decode('utf-8').strip().split(':')[0])
print(f"函数起始行: {line_num}")

# 读取函数开头20行
stdin, stdout, stderr = client.exec_command(f'sed -n {line_num},{line_num+25}p /opt/scis/components.py')
print("\n=== 函数开头 ===")
print(repr(stdout.read().decode('utf-8')))

# 读取分组标题渲染部分
stdin, stdout, stderr = client.exec_command(f'sed -n {line_num+60},{line_num+100}p /opt/scis/components.py')
print("\n=== 分组渲染部分 ===")
print(repr(stdout.read().decode('utf-8'))[:2000])

client.close()
