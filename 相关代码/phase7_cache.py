import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取 streamlit_app.py
stdin, stdout, stderr = client.exec_command('cat /opt/scis/streamlit_app.py')
content = stdout.read().decode('utf-8')

# Step 1: 在导入组件后添加缓存包装函数
marker = '# === User Auth Config ==='

cache_funcs = '''# === Data Caching (Phase 7) ===
import time

# Cache TTL: 5 minutes for data files, 1 hour for static lookups
@st.cache_data(ttl=300, show_spinner=False)
def cached_load_home_cache():
    return load_home_cache()

@st.cache_data(ttl=300, show_spinner=False)
def cached_load_sales_daily():
    return load_sales_daily()

@st.cache_data(ttl=300, show_spinner=False)
def cached_load_sku_master():
    return load_sku_master()

@st.cache_data(ttl=300, show_spinner=False)
def cached_load_warehouse_master():
    return load_warehouse_master()

@st.cache_data(ttl=300, show_spinner=False)
def cached_load_demand_forecast():
    return load_demand_forecast()

@st.cache_data(ttl=300, show_spinner=False)
def cached_load_replenishment_plan():
    return load_replenishment_plan()

@st.cache_data(ttl=300, show_spinner=False)
def cached_load_inventory_snapshot():
    return load_inventory_snapshot()

@st.cache_data(ttl=300, show_spinner=False)
def cached_load_transfer_recommendation():
    return load_transfer_recommendation()

@st.cache_data(ttl=300, show_spinner=False)
def cached_load_logistics_tracking():
    return load_logistics_tracking()

@st.cache_data(ttl=300, show_spinner=False)
def cached_load_purchase_orders():
    return load_purchase_orders()

@st.cache_data(ttl=300, show_spinner=False)
def cached_load_inventory_health_report():
    return load_inventory_health_report()

@st.cache_data(ttl=60, show_spinner=False)
def cached_compute_kpis():
    return compute_kpis()


'''

content = content.replace(marker, cache_funcs + marker, 1)
print("OK: cache wrappers added")

# Step 2: 替换所有页面中的数据加载调用为缓存版本
replacements = {
    'load_home_cache()': 'cached_load_home_cache()',
    'load_sales_daily()': 'cached_load_sales_daily()',
    'load_sku_master()': 'cached_load_sku_master()',
    'load_warehouse_master()': 'cached_load_warehouse_master()',
    'load_demand_forecast()': 'cached_load_demand_forecast()',
    'load_replenishment_plan()': 'cached_load_replenishment_plan()',
    'load_inventory_snapshot()': 'cached_load_inventory_snapshot()',
    'load_transfer_recommendation()': 'cached_load_transfer_recommendation()',
    'load_logistics_tracking()': 'cached_load_logistics_tracking()',
    'load_purchase_orders()': 'cached_load_purchase_orders()',
    'load_inventory_health_report()': 'cached_load_inventory_health_report()',
    'compute_kpis()': 'cached_compute_kpis()',
}

for old, new in replacements.items():
    content = content.replace(old, new)

print("OK: all load calls replaced with cached versions")

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
