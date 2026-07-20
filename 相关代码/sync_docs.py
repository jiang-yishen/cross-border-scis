import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 下载更新后的文档到本地
sftp = client.open_sftp()
sftp.get('/opt/scis/项目问题记录文档.md', 
         'C:/Users/11363/Desktop/供应链计划面试/供应链优化项目/项目问题记录文档.md')
print("OK: 项目问题记录文档已同步到本地")

sftp.get('/opt/scis/跨境海外仓供应链智能决策系统_项目汇报.docx',
         'C:/Users/11363/Desktop/供应链计划面试/供应链优化项目/跨境海外仓供应链智能决策系统_项目汇报.docx')
print("OK: 项目汇报文档已同步到本地")

client.close()
