import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

print("=== page_guide (1900-1925) ===")
stdin, stdout, stderr = client.exec_command('sed -n 1900,1925p /opt/scis/streamlit_app.py')
print(stdout.read().decode('utf-8'))

print("\n=== page_ops_center (2030-2055) ===")
stdin, stdout, stderr = client.exec_command('sed -n 2030,2055p /opt/scis/streamlit_app.py')
print(stdout.read().decode('utf-8'))

client.close()
