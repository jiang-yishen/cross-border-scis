import paramiko
import base64

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

stdin, stdout, stderr = client.exec_command('cat /opt/scis/components.py')
content = stdout.read().decode('utf-8')

old2 = '''        # 渲染分组导航\r\n\r\n        for group in NAV_GROUPS:\r\n\r\n            # 分组标题（居中 + 两侧装饰线）'''

new2 = '''        # 获取当前用户可访问的页面
        allowed_pages = get_allowed_pages()
        allowed_keys = {p["key"] for p in allowed_pages}

        # 渲染分组导航（权限过滤）
        for group in NAV_GROUPS:
            # 过滤该分组下允许的页面
            group_pages = [pg for pg in group["pages"] if pg["key"] in allowed_keys]
            if not group_pages:
                continue

            # 分组标题（居中 + 两侧装饰线）'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("✅ 2. 导航权限过滤")
else:
    print("❌ 2. 未找到")

# 同时检查内层循环是否已经修复（从之前的修改）
if 'for pg in group_pages:' in content:
    print("✅ 3. 内层循环已修复")
else:
    print("⚠️ 3. 内层循环需要检查")

if 'if allowed_pages:' in content and 'return None' in content:
    print("✅ 4. 返回语句已修复")
else:
    print("⚠️ 4. 返回语句需要检查")

encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
stdin, stdout, stderr = client.exec_command(f'echo "{encoded}" | base64 -d > /opt/scis/components.py')
err = stderr.read().decode('utf-8')
if err.strip():
    print("ERR:", err)
else:
    print("✅ 文件已写入")

client.close()
print("\n完成")
