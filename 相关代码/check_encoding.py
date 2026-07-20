import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查文件编码和中文内容
stdin, stdout, stderr = client.exec_command('file /opt/scis/components.py')
print("文件类型:", stdout.read().decode('utf-8').strip())

stdin, stdout, stderr = client.exec_command('head -5 /opt/scis/components.py | od -c | head -5')
print("\n前5行十六进制:", stdout.read().decode('utf-8').strip())

stdin, stdout, stderr = client.exec_command('grep "核心运营" /opt/scis/components.py')
print("\n中文grep:", stdout.read().decode('utf-8').strip())

client.close()
