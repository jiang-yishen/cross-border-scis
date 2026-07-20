import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 精确删除第698行（空的 def sidebar_navigation():）
stdin, stdout, stderr = client.exec_command('sed -i "698d" /opt/scis/components.py')
err = stderr.read().decode('utf-8')
if err.strip():
    print("ERR:", err)
else:
    print("✅ 删除第698行成功")

# 验证修复
stdin, stdout, stderr = client.exec_command('sed -n 695,705p /opt/scis/components.py')
print("\n=== 修复后 695-705 ===")
print(stdout.read().decode('utf-8'))

# 重启服务
client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
