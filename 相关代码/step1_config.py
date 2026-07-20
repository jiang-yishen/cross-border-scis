import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# Step 1: 在第 38 行后插入用户配置
config_block = '''

# === User Auth Config ===
USERS = {
    "admin":   {"password": "jwyjys5210", "role": "admin",   "name": "Admin"},
    "planner": {"password": "scis2024", "role": "planner", "name": "Planner"},
    "viewer":  {"password": "scis2024", "role": "viewer",  "name": "Viewer"},
}

ROLE_PERMISSIONS = {
    "admin":   ["home","import","forecast","inventory","replenish","transfer","logistics","guide","ops"],
    "planner": ["home","import","forecast","inventory","replenish","transfer","logistics","guide"],
    "viewer":  ["home","guide"],
}
'''

# 用 Python 在服务器上执行插入
stdin, stdout, stderr = client.exec_command(f"""python3 -c "
with open('/opt/scis/streamlit_app.py', 'r') as f:
    lines = f.readlines()

# 在第 38 行（索引 37）后插入配置
insert_lines = {repr(config_block)}.split('\\n')
for i, line in enumerate(insert_lines):
    if line:
        lines.insert(38 + i, line + '\\n')

with open('/opt/scis/streamlit_app.py', 'w') as f:
    f.writelines(lines)
print('OK: config inserted')
""")
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')
print(out)
if err.strip():
    print("ERR:", err)

client.close()
