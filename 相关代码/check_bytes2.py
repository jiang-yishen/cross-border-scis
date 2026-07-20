import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 在服务器上创建临时检查脚本
script = """import re
with open('/opt/scis/components.py', 'rb') as f:
    data = f.read()

idx = data.find('核心运营'.encode('utf-8'))
print('核心运营 at', idx)
if idx > 0:
    print('周围:', repr(data[max(0,idx-10):idx+20]))

print('文件大小:', len(data), 'bytes')

# 检查是否混合了UTF-8和Latin-1
try:
    text = data.decode('utf-8')
    print('UTF-8解码: OK')
except Exception as e:
    print('UTF-8解码失败:', e)

# 检查是否有double-encoded UTF-8
idx2 = data.find('\\xe6\\x00\\xa0\\x00'.encode('latin-1'))
print('double-encode at', idx2)
"""

sftp = client.open_sftp()
with sftp.file('/tmp/check_bytes.py', 'w') as f:
    f.write(script.encode('utf-8'))

stdin, stdout, stderr = client.exec_command('python3 /tmp/check_bytes.py')
print(stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("ERR:", err)

client.close()
