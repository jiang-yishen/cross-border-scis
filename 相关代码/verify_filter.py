import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 验证代码
stdin, stdout, stderr = client.exec_command('python3 -m py_compile /opt/scis/components.py && echo "SYNTAX OK"')
out = stdout.read().decode('utf-8').strip()
err = stderr.read().decode('utf-8').strip()
print("语法:", out)
if err:
    print("ERR:", err)

# 读取修改区域
stdin, stdout, stderr = client.exec_command('sed -n 413,435p /opt/scis/components.py')
print("\n修改区域:")
print(stdout.read().decode('utf-8'))

client.close()
