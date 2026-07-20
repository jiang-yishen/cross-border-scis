import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=15)

# 读取当前文件
sftp = client.open_sftp()
with sftp.file('/opt/scis/components.py', 'r') as f:
    content = f.read().decode('utf-8')

# 暴力测试：在</style>前插入全局红色边框CSS
if 'border: 3px solid red' not in content:
    content = content.replace('</style>', '    /* 暴力测试：所有按钮红色边框 */\n    button { border: 3px solid red !important; }\n    </style>')

with sftp.file('/opt/scis/components.py', 'w') as f:
    f.write(content.encode('utf-8'))

sftp.close()

stdin, stdout, stderr = client.exec_command('sudo systemctl restart scis-streamlit')
print('Restart:', stdout.read().decode().strip(), stderr.read().decode().strip())
client.close()
print('Done')
