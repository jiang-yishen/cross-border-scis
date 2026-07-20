import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 1. 从 Gitee 下载干净的 components.py
stdin, stdout, stderr = client.exec_command('curl -sL https://gitee.com/jiang-yishen/cross-border-scis/raw/main/components.py -o /opt/scis/components.py')
err = stderr.read().decode('utf-8')
if err.strip():
    print("curl ERR:", err)
else:
    print("✅ 下载完成")

# 验证下载成功
stdin, stdout, stderr = client.exec_command('wc -c /opt/scis/components.py')
print("文件大小:", stdout.read().decode('utf-8').strip())

client.close()
