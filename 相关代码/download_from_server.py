import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

sftp = client.open_sftp()
sftp.get('/opt/scis/streamlit_app.py', 'C:/Users/11363/Desktop/供应链计划面试/供应链优化项目/streamlit_app.py')
print('OK: downloaded streamlit_app.py')

# 同时下载 components.py
sftp.get('/opt/scis/components.py', 'C:/Users/11363/Desktop/供应链计划面试/供应链优化项目/components.py')
print('OK: downloaded components.py')

client.close()
