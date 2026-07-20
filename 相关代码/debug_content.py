import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

stdin, stdout, stderr = client.exec_command('cat /opt/scis/components.py')
content = stdout.read().decode('utf-8')
client.close()

# 查找关键文本的位置
markers = [
    '""", unsafe_allow_html=True)',
    '初始化 session state',
    '渲染分组导航',
]

for m in markers:
    idx = content.find(m)
    print(f"'{m[:30]}...' at {idx}")
    if idx != -1:
        print(f"  前后: {repr(content[max(0,idx-20):idx+50])}")

# 检查换行符
print(f"\n换行符统计: \\n={content.count(chr(10))}, \\r={content.count(chr(13))}")

# 检查具体区域
idx = content.find('初始化 session state')
if idx != -1:
    print(f"\n精确内容: {repr(content[idx-50:idx+80])}")
