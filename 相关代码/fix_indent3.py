import paramiko
import base64

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

stdin, stdout, stderr = client.exec_command('cat /opt/scis/components.py')
content = stdout.read().decode('utf-8')

# 用 line-by-line 方式修复
lines = content.split('\r\n')
print(f"总行数: {len(lines)}")

# 找到并修复问题区域
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # 检查是否是 "def sidebar_navigation():" 后面紧跟 "for g in NAV_GROUPS:"
    if line.strip() == 'def sidebar_navigation():' and i + 2 < len(lines) and 'for g in NAV_GROUPS' in lines[i + 2]:
        # 跳过这个错误的函数定义和接下来的3行（for + NAV_PAGES.extend + 空行）
        fixed_lines.append(line)  # 保留正确的 def sidebar_navigation():
        i += 1
        # 跳过 for g in NAV_GROUPS: 和 NAV_PAGES.extend 和空行
        while i < len(lines) and (lines[i].strip() == '' or 'for g in' in lines[i] or 'NAV_PAGES.extend' in lines[i]):
            i += 1
        continue
    fixed_lines.append(line)
    i += 1

new_content = '\r\n'.join(fixed_lines)
print(f"修复后行数: {len(fixed_lines)}")

encoded = base64.b64encode(new_content.encode('utf-8')).decode('ascii')
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /opt/scis/components.py')
err = stderr.read().decode('utf-8')
if err.strip():
    print("ERR:", err)
else:
    print("✅ 文件已写入")

client.exec_command('sudo systemctl restart scis-streamlit')
print("🔄 服务已重启")

client.close()
