import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

stdin, stdout, stderr = client.exec_command('grep -n "渲染分组导航" /opt/scis/components.py')
line = stdout.read().decode('utf-8').strip()
print("line:", line)
linenum = int(line.split(':')[0])

stdin, stdout, stderr = client.exec_command(f'sed -n {linenum-2},{linenum+6}p /opt/scis/components.py')
print(repr(stdout.read().decode('utf-8')))

client.close()
