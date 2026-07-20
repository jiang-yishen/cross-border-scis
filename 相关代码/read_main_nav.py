import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

print("=== main() 函数 ===")
stdin, stdout, stderr = client.exec_command('sed -n 2310,2370p /opt/scis/streamlit_app.py')
print(stdout.read().decode('utf-8'))

print("\n=== sidebar_navigation() 函数 ===")
stdin, stdout, stderr = client.exec_command('sed -n 292,360p /opt/scis/components.py')
print(stdout.read().decode('utf-8'))

client.close()
