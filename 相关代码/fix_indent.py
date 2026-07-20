import paramiko
import base64

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

stdin, stdout, stderr = client.exec_command('cat /opt/scis/components.py')
content = stdout.read().decode('utf-8')

# 删除多余的 NAV_PAGES 构建代码
old = '''    return [p for p in NAV_PAGES if p["key"] in allowed_keys]


def sidebar_navigation():

for g in NAV_GROUPS:

    NAV_PAGES.extend(g["pages"])



def sidebar_navigation():'''

new = '''    return [p for p in NAV_PAGES if p["key"] in allowed_keys]


def sidebar_navigation():'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ 修复成功")
else:
    print("❌ 未找到匹配")

encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /opt/scis/components.py')
err = stderr.read().decode('utf-8')
if err.strip():
    print("ERR:", err)
else:
    print("✅ 文件已写入")

# 重启
client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
