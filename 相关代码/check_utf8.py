import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

script = """
import codecs

with open('/opt/scis/components.py', 'rb') as f:
    data = f.read()

# 检查所有中文字符是否有效UTF-8
invalid = []
for i, b in enumerate(data):
    if b >= 0x80:
        # 检查是否是有效的UTF-8序列开始
        if b >= 0xC0:
            # 多字节序列
            if b >= 0xF0:
                length = 4
            elif b >= 0xE0:
                length = 3
            elif b >= 0xC0:
                length = 2
            else:
                invalid.append((i, b))
                continue
            # 检查后续字节
            valid = True
            for j in range(1, length):
                if i + j >= len(data) or not (0x80 <= data[i+j] < 0xC0):
                    valid = False
                    break
            if not valid:
                invalid.append((i, b, 'invalid continuation'))

print('Invalid UTF-8 sequences:', len(invalid))
for item in invalid[:10]:
    print(item)

# 检查文件中的CRLF和LF混合
print('CRLF count:', data.count(b'\\r\\n'))
print('LF-only count:', data.count(b'\\n') - data.count(b'\\r\\n'))
print('CR-only count:', data.count(b'\\r') - data.count(b'\\r\\n'))

# 如果文件完全正常，可能是服务器环境缺少UTF-8 locale
"""

sftp = client.open_sftp()
with sftp.file('/tmp/check_utf8.py', 'w') as f:
    f.write(script.encode('utf-8'))

stdin, stdout, stderr = client.exec_command('python3 /tmp/check_utf8.py')
print(stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("ERR:", err)

client.close()
