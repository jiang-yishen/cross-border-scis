import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取文件
stdin, stdout, stderr = client.exec_command('cat /opt/scis/streamlit_app.py')
content = stdout.read().decode('utf-8')

# 修复1: 把所有 cached_cached_ 改为 cached_
content = content.replace('cached_cached_', 'cached_')
print("OK: fixed cached_cached_ -> cached_")

# 修复2: 缓存函数定义内部应该是 return compute_kpis() 而不是 return cached_compute_kpis()
# 找到缓存函数定义区域并修复内部调用
for func_name in ['cached_load_home_cache', 'cached_load_sales_daily', 'cached_load_sku_master', 
                  'cached_load_warehouse_master', 'cached_load_demand_forecast', 
                  'cached_load_replenishment_plan', 'cached_load_inventory_snapshot',
                  'cached_load_transfer_recommendation', 'cached_load_logistics_tracking',
                  'cached_load_purchase_orders', 'cached_load_inventory_health_report',
                  'cached_compute_kpis']:
    old = f'def {func_name}():\n    return {func_name}()'
    new = f'def {func_name}():\n    return {func_name.replace("cached_", "")}()'
    if old in content:
        content = content.replace(old, new, 1)
        print(f"OK: fixed {func_name} internal call")
    else:
        print(f"CHECK: {func_name} pattern not found as expected")

# 写回
sftp = client.open_sftp()
with sftp.file('/opt/scis/streamlit_app.py', 'w') as f:
    f.write(content.encode('utf-8'))
print("OK: file written")

# 语法检查
stdin, stdout, stderr = client.exec_command('python3 -m py_compile /opt/scis/streamlit_app.py && echo "SYNTAX OK"')
print("语法:", stdout.read().decode('utf-8').strip())

client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
