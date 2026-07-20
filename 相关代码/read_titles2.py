import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

print("=== page_guide (1880-1910) ===")
stdin, stdout, stderr = client.exec_command('sed -n 1880,1910p /opt/scis/streamlit_app.py')
print(stdout.read().decode('utf-8'))

print("\n=== page_ops_center (2000-2035) ===")
stdin, stdout, stderr = client.exec_command('sed -n 2000,2035p /opt/scis/streamlit_app.py')
print(stdout.read().decode('utf-8'))

client.close()
