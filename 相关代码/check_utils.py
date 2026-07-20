import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查 utils.py 中的 load 函数
stdin, stdout, stderr = client.exec_command('grep -n "def load_" /opt/scis/utils.py')
print("utils.py 数据加载函数:")
print(stdout.read().decode('utf-8'))

client.close()
