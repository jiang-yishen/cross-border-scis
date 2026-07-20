import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查是否有备份保留了 Phase 1-5 的修改
stdin, stdout, stderr = client.exec_command('find /opt/scis -name "*.backup*" -o -name "*.bak" 2>/dev/null | head -20')
print("备份文件:")
print(stdout.read().decode('utf-8'))

# 检查 git stash / reflog
stdin, stdout, stderr = client.exec_command('cd /opt/scis && git stash list 2>/dev/null || echo "no stash"')
print("\nstash:")
print(stdout.read().decode('utf-8'))

stdin, stdout, stderr = client.exec_command('cd /opt/scis && git reflog --all 2>/dev/null | head -20')
print("\nreflog:")
print(stdout.read().decode('utf-8'))

# 检查 git 分支
stdin, stdout, stderr = client.exec_command('cd /opt/scis && git branch -a')
print("\n分支:")
print(stdout.read().decode('utf-8'))

client.close()
