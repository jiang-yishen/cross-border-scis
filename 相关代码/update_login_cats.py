import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取文件
stdin, stdout, stderr = client.exec_command('cat /opt/scis/streamlit_app.py')
content = stdout.read().decode('utf-8')

# 找到登录页面左侧区域并替换为更丰富的暖色调+小猫图案
old = '''st.markdown("<div style=\\"display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;min-height:500px;background:linear-gradient(135deg,#FFF8E7 0%,#FFE4C4 30%,#DEB887 70%,#CD853F 100%);border-radius:24px;padding:40px;color:#5D4037;text-align:center;box-shadow:0 8px 32px rgba(139,69,19,0.15);\\\"><div style=\\"font-size:80px;margin-bottom:16px;\\\">🐱</div><h1 style=\\"color:#5D4037;margin:0 0 8px 0;font-size:26px;font-weight:700;\\\">跨境海外仓</h1><h2 style=\\"color:#8D6E63;margin:0 0 20px 0;font-size:18px;font-weight:500;\\\">供应链智能决策系统</h2><p style=\\"color:#A1887F;margin:0 0 24px 0;font-size:13px;\\\">🐾 让库存管理更轻松，让决策更智能 🐾</p><div style=\\"margin-top:24px;display:flex;gap:16px;justify-content:center;\\\"><div style=\\"background:rgba(255,255,255,0.6);border-radius:16px;padding:16px 20px;text-align:center;backdrop-filter:blur(10px);box-shadow:0 4px 12px rgba(139,69,19,0.1);\\\"><div style=\\"font-size:28px;font-weight:700;color:#6D4C41;\\\">1,100+</div><div style=\\"font-size:11px;color:#8D6E63;\\\">📦 SKU覆盖</div></div><div style=\\"background:rgba(255,255,255,0.6);border-radius:16px;padding:16px 20px;text-align:center;backdrop-filter:blur(10px);box-shadow:0 4px 12px rgba(139,69,19,0.1);\\\"><div style=\\"font-size:28px;font-weight:700;color:#6D4C41;\\\">6</div><div style=\\"font-size:11px;color:#8D6E63;\\\">🌍 海外仓库</div></div><div style=\\"background:rgba(255,255,255,0.6);border-radius:16px;padding:16px 20px;text-align:center;backdrop-filter:blur(10px);box-shadow:0 4px 12px rgba(139,69,19,0.1);\\\"><div style=\\"font-size:28px;font-weight:700;color:#6D4C41;\\\">2026</div><div style=\\"font-size:11px;color:#8D6E63;\\\">🚀 系统版本</div></div></div><div style=\\"margin-top:28px;font-size:12px;color:#A1887F;\\\">💰 等工资到账中... 不对，等库存优化中... 💰</div></div>", unsafe_allow_html=True)'''

new = '''st.markdown("<div style=\\"display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;min-height:500px;background:linear-gradient(135deg,#FFF8E7 0%,#FFE4C4 30%,#DEB887 70%,#CD853F 100%);border-radius:24px;padding:40px;color:#5D4037;text-align:center;box-shadow:0 8px 32px rgba(139,69,19,0.15);position:relative;overflow:hidden;\\\"><div style=\\"position:absolute;top:20px;left:30px;font-size:32px;opacity:0.4;\\\">🐱</div><div style=\\"position:absolute;top:60px;right:40px;font-size:24px;opacity:0.3;\\\">🐾</div><div style=\\"position:absolute;bottom:80px;left:50px;font-size:28px;opacity:0.3;\\\">🐟</div><div style=\\"position:absolute;bottom:40px;right:60px;font-size:20px;opacity:0.4;\\\">🐱</div><div style=\\"position:absolute;top:150px;left:20px;font-size:18px;opacity:0.25;\\\">🐾</div><div style=\\"position:absolute;top:200px;right:25px;font-size:22px;opacity:0.25;\\\">🐱</div><div style=\\"position:relative;z-index:1;\\\"><div style=\\"font-size:80px;margin-bottom:16px;\\\">🐱</div><h1 style=\\"color:#5D4037;margin:0 0 8px 0;font-size:26px;font-weight:700;\\\">跨境海外仓</h1><h2 style=\\"color:#8D6E63;margin:0 0 20px 0;font-size:18px;font-weight:500;\\\">供应链智能决策系统</h2><p style=\\"color:#A1887F;margin:0 0 24px 0;font-size:13px;\\\">🐾 让库存管理更轻松，让决策更智能 🐾</p><div style=\\"margin-top:24px;display:flex;gap:16px;justify-content:center;\\\"><div style=\\"background:rgba(255,248,231,0.85);border-radius:16px;padding:16px 20px;text-align:center;backdrop-filter:blur(10px);box-shadow:0 4px 12px rgba(139,69,19,0.12);border:1px solid rgba(222,184,135,0.4);\\\"><div style=\\"font-size:28px;font-weight:700;color:#6D4C41;\\\">1,100+</div><div style=\\"font-size:11px;color:#8D6E63;\\\">📦 SKU覆盖</div></div><div style=\\"background:rgba(255,248,231,0.85);border-radius:16px;padding:16px 20px;text-align:center;backdrop-filter:blur(10px);box-shadow:0 4px 12px rgba(139,69,19,0.12);border:1px solid rgba(222,184,135,0.4);\\\"><div style=\\"font-size:28px;font-weight:700;color:#6D4C41;\\\">6</div><div style=\\"font-size:11px;color:#8D6E63;\\\">🌍 海外仓库</div></div><div style=\\"background:rgba(255,248,231,0.85);border-radius:16px;padding:16px 20px;text-align:center;backdrop-filter:blur(10px);box-shadow:0 4px 12px rgba(139,69,19,0.12);border:1px solid rgba(222,184,135,0.4);\\\"><div style=\\"font-size:28px;font-weight:700;color:#6D4C41;\\\">2026</div><div style=\\"font-size:11px;color:#8D6E63;\\\">🚀 系统版本</div></div></div><div style=\\"margin-top:28px;font-size:12px;color:#A1887F;\\\">💰 等库存优化中... 💰</div></div></div>", unsafe_allow_html=True)'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: login page updated with cat decorations and warm cards")
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
