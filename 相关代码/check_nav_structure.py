import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# Step 1: 检查 components.py 中 sidebar_navigation() 的导航循环结构
stdin, stdout, stderr = client.exec_command('grep -n "for group in NAV_GROUPS" /opt/scis/components.py')
print("导航循环:", stdout.read().decode('utf-8').strip())

stdin, stdout, stderr = client.exec_command('grep -n "for pg in" /opt/scis/components.py')
print("页面循环:", stdout.read().decode('utf-8').strip())

# Step 2: 在 components.py 中，NAV_PAGES 定义后添加权限过滤辅助函数
stdin, stdout, stderr = client.exec_command('grep -n "NAV_PAGES = \[" /opt/scis/components.py')
print("NAV_PAGES:", stdout.read().decode('utf-8').strip())

client.close()
