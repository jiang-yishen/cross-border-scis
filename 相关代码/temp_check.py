import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=15)
stdin, stdout, stderr = c.exec_command('cd /opt/scis && .venv/bin/python -m streamlit --version 2>/dev/null || python3 -m streamlit --version')
print('VERSION:', stdout.read().decode().strip())
print('ERR:', stderr.read().decode().strip())
c.close()
