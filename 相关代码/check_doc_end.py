import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查文档末尾
stdin, stdout, stderr = client.exec_command('tail -100 /opt/scis/项目问题记录文档.md')
print("=== 文档末尾 ===")
print(stdout.read().decode('utf-8'))

# 检查 Q027 是否存在
stdin, stdout, stderr = client.exec_command('grep -n "Q027" /opt/scis/项目问题记录文档.md')
print("\n=== Q027 查找 ===")
print(stdout.read().decode('utf-8'))

client.close()
