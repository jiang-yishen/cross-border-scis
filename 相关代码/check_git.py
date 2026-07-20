import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 用 git 恢复干净的 components.py（Phase 5 完成时的版本）
stdin, stdout, stderr = client.exec_command('cd /opt/scis && git log --oneline -5')
print("=== git log ===")
print(stdout.read().decode('utf-8'))

# 检查是否有干净的备份
stdin, stdout, stderr = client.exec_command('ls /opt/scis/*.bak 2>/dev/null || echo "无备份"')
print("\n=== 备份文件 ===")
print(stdout.read().decode('utf-8'))

client.close()
