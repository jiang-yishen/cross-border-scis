import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取完整 components.py
print("读取 components.py...")
sftp = client.open_sftp()
with sftp.file('/opt/scis/components.py', 'r') as f:
    content = f.read().decode('utf-8')

# 保存到本地备份
with open('components_backup_phase6.py', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"已备份到本地，共 {len(content)} 字符")

client.close()
print("读取完成")
