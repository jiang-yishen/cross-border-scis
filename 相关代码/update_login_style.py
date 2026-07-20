import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取文件
stdin, stdout, stderr = client.exec_command('cat /opt/scis/streamlit_app.py')
content = stdout.read().decode('utf-8')

# 替换左侧装饰区域为暖色调可爱风格
old_login = '''        st.markdown("<div style=\\"display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;min-height:500px;background:linear-gradient(135deg,#1B4965 0%,#457B9D 100%);border-radius:16px;padding:40px;color:white;text-align:center;\\\"><div style=\\"font-size:64px;margin-bottom:20px;\\\">🚢</div><h1 style=\\"color:white;margin:0 0 12px 0;font-size:28px;\\\">Cross-Border Warehouse</h1><h2 style=\\"color:white;margin:0 0 16px 0;font-size:20px;opacity:0.9;\\\">SCIS System</h2><div style=\\"margin-top:32px;display:flex;gap:24px;justify-content:center;\\\"><div style=\\"text-align:center;\\\"><div style=\\"font-size:24px;font-weight:700;\\\">1,100+</div><div style=\\"font-size:12px;opacity:0.7;\\\">SKUs</div></div><div style=\\"text-align:center;\\\"><div style=\\"font-size:24px;font-weight:700;\\\">6</div><div style=\\"font-size:12px;opacity:0.7;\\\">Warehouses</div></div><div style=\\"text-align:center;\\\"><div style=\\"font-size:24px;font-weight:700;\\\">2026</div><div style=\\"font-size:12px;opacity:0.7;\\\">Version</div></div></div></div>", unsafe_allow_html=True)'''

new_login = '''        st.markdown("<div style=\\"display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;min-height:500px;background:linear-gradient(135deg,#FFF8E7 0%,#FFE4C4 30%,#DEB887 70%,#CD853F 100%);border-radius:24px;padding:40px;color:#5D4037;text-align:center;box-shadow:0 8px 32px rgba(139,69,19,0.15);\\\"><div style=\\"font-size:80px;margin-bottom:16px;\\\">🐱</div><h1 style=\\"color:#5D4037;margin:0 0 8px 0;font-size:26px;font-weight:700;\\\">跨境海外仓</h1><h2 style=\\"color:#8D6E63;margin:0 0 20px 0;font-size:18px;font-weight:500;\\\">供应链智能决策系统</h2><p style=\\"color:#A1887F;margin:0 0 24px 0;font-size:13px;\\\">🐾 让库存管理更轻松，让决策更智能 🐾</p><div style=\\"margin-top:24px;display:flex;gap:16px;justify-content:center;\\\"><div style=\\"background:rgba(255,255,255,0.6);border-radius:16px;padding:16px 20px;text-align:center;backdrop-filter:blur(10px);box-shadow:0 4px 12px rgba(139,69,19,0.1);\\\"><div style=\\"font-size:28px;font-weight:700;color:#6D4C41;\\\">1,100+</div><div style=\\"font-size:11px;color:#8D6E63;\\\">📦 SKU覆盖</div></div><div style=\\"background:rgba(255,255,255,0.6);border-radius:16px;padding:16px 20px;text-align:center;backdrop-filter:blur(10px);box-shadow:0 4px 12px rgba(139,69,19,0.1);\\\"><div style=\\"font-size:28px;font-weight:700;color:#6D4C41;\\\">6</div><div style=\\"font-size:11px;color:#8D6E63;\\\">🌍 海外仓库</div></div><div style=\\"background:rgba(255,255,255,0.6);border-radius:16px;padding:16px 20px;text-align:center;backdrop-filter:blur(10px);box-shadow:0 4px 12px rgba(139,69,19,0.1);\\\"><div style=\\"font-size:28px;font-weight:700;color:#6D4C41;\\\">2026</div><div style=\\"font-size:11px;color:#8D6E63;\\\">🚀 系统版本</div></div></div><div style=\\"margin-top:28px;font-size:12px;color:#A1887F;\\\">💰 等工资到账中... 不对，等库存优化中... 💰</div></div>", unsafe_allow_html=True)'''

if old_login in content:
    content = content.replace(old_login, new_login, 1)
    print("OK: login page updated to warm cute style")
else:
    print("FAIL: old login not found")

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
