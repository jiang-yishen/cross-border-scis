import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

stdin, stdout, stderr = client.exec_command('sed -n 695,705p /opt/scis/components.py')
print(repr(stdout.read().decode('utf-8')))

client.close()
