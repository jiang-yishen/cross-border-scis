import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 备份当前文件
client.exec_command('cp /opt/scis/streamlit_app.py /opt/scis/streamlit_app.py.backup.phase5')
client.exec_command('cp /opt/scis/components.py /opt/scis/components.py.backup.phase5')
print("✅ 备份完成")

# 检查当前导入语句结构
stdin, stdout, stderr = client.exec_command("grep -n -A 5 'from components import' /opt/scis/streamlit_app.py | head -20")
print("\n=== 导入语句 ===")
print(stdout.read().decode('utf-8'))

# 检查 main() 函数
stdin, stdout, stderr = client.exec_command('grep -n "def main" /opt/scis/streamlit_app.py')
print("\n=== main() 行号 ===")
print(stdout.read().decode('utf-8').strip())

client.close()
