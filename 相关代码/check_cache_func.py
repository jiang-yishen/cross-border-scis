import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 检查 cached_compute_kpis 是否定义
stdin, stdout, stderr = client.exec_command('grep -n "def cached_compute_kpis" /opt/scis/streamlit_app.py')
print("cached_compute_kpis 定义:", stdout.read().decode('utf-8').strip() or "NOT FOUND")

# 检查 page_home 中调用
stdin, stdout, stderr = client.exec_command('grep -n "cached_compute_kpis" /opt/scis/streamlit_app.py')
print("\ncached_compute_kpis 所有出现:")
print(stdout.read().decode('utf-8'))

client.close()
