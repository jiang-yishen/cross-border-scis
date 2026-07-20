import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查当前页面函数中数据加载的逻辑
stdin, stdout, stderr = client.exec_command('grep -n "def page_" /opt/scis/streamlit_app.py')
print("页面函数:")
print(stdout.read().decode('utf-8'))

# 检查是否有 compute_kpis 等数据加载函数
stdin, stdout, stderr = client.exec_command('grep -n "def compute_kpis" /opt/scis/streamlit_app.py')
print("\ncompute_kpis:", stdout.read().decode('utf-8').strip())

# 检查数据加载方式
stdin, stdout, stderr = client.exec_command('grep -n "load_" /opt/scis/streamlit_app.py | head -20')
print("\n数据加载:")
print(stdout.read().decode('utf-8'))

client.close()
