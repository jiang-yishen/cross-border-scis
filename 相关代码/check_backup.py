import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查是否有 git 仓库和备份
stdin, stdout, stderr = client.exec_command('cd /opt/scis && ls -la .git 2>/dev/null && echo "有git" || echo "无git"')
print("git:", stdout.read().decode('utf-8').strip())

# 检查是否有备份文件
stdin, stdout, stderr = client.exec_command('ls /opt/scis/*.bak /opt/scis/*backup* 2>/dev/null || echo "无备份"')
print("备份:", stdout.read().decode('utf-8').strip())

# 检查 git 分支
stdin, stdout, stderr = client.exec_command('cd /opt/scis && git branch -a 2>/dev/null || echo "无git"')
print("分支:", stdout.read().decode('utf-8').strip())

# 检查 git log
stdin, stdout, stderr = client.exec_command('cd /opt/scis && git log --oneline -10 2>/dev/null || echo "无git"')
print("log:", stdout.read().decode('utf-8').strip())

client.close()
