import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查文件的字节内容
stdin, stdout, stderr = client.exec_command('python3 -c "\nwith open(\"/opt/scis/components.py\", \"rb\") as f:\n    data = f.read()\n    # 检查几个中文字符的位置\n    idx = data.find(b\"\\xe6\\xa0\\xb8\\xe5\\xbf\\x83\\xe8\\xbf\\x90\\xe8\\x90\\xa5\")\n    print(\"核心运营 at\", idx)\n    if idx > 0:\n        print(\"周围:", repr(data[idx-20:idx+30]))\n    \n    # 检查文件大小\n    print(\"文件大小:\", len(data), \"bytes\")\n    \n    # 检查是否有乱码特征（GBK编码的UTF-8字节）\n    for i in range(len(data)-2):\n        if data[i] > 0x7f and data[i+1] < 0x80 and data[i+2] > 0x7f:\n            print(\"可疑字节 at\", i, \":\", repr(data[i:i+6]))\n            break\n"')
print(stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("ERR:", err)

client.close()
