import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查 streamlit_app.py 中 main() 的 session_state 初始化
stdin, stdout, stderr = client.exec_command('grep -n "user_logged_in" /opt/scis/streamlit_app.py')
print("streamlit_app.py 中的 user_logged_in:")
print(stdout.read().decode('utf-8'))

# 检查 components.py 中是否有其他地方设置 user_logged_in
stdin, stdout, stderr = client.exec_command('grep -n "user_logged_in" /opt/scis/components.py')
print("\ncomponents.py 中的 user_logged_in:")
print(stdout.read().decode('utf-8'))

client.close()
