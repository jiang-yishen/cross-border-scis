import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 语法检查
stdin, stdout, stderr = client.exec_command('python3 -m py_compile /opt/scis/streamlit_app.py && echo "SYNTAX OK"')
out = stdout.read().decode('utf-8').strip()
err = stderr.read().decode('utf-8').strip()
print("语法:", out)
if err:
    print("ERR:", err)

# 检查关键行
stdin, stdout, stderr = client.exec_command('sed -n 34,42p /opt/scis/streamlit_app.py')
print("\n导入区域:")
print(stdout.read().decode('utf-8'))

client.close()
