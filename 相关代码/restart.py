import paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)
c.exec_command('sudo systemctl restart scis-streamlit')
c.close()
print('🔄 服务已重启')
