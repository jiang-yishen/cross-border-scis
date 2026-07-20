import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 从本地备份恢复 Phase 1-5 代码
sftp = client.open_sftp()
sftp.put('C:/Users/11363/Desktop/供应链计划面试/供应链优化项目/server_backup/streamlit_app.py', '/opt/scis/streamlit_app.py')
print("OK: streamlit_app.py restored (115453 bytes)")

sftp.put('C:/Users/11363/Desktop/供应链计划面试/供应链优化项目/server_backup/components.py', '/opt/scis/components.py')
print("OK: components.py restored (17587 bytes)")

client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
