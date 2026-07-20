import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 创建 Locust 压测脚本
locust_script = '''from locust import HttpUser, task, between
import random

class SCISUser(HttpUser):
    """模拟用户访问 SCIS 系统"""
    wait_time = between(1, 5)  # 用户间隔 1-5 秒
    host = "http://47.239.173.51:8501"
    
    def on_start(self):
        """用户启动时执行：登录"""
        # 随机选择账号
        accounts = [
            {"username": "admin", "password": "jwyjys5210"},
            {"username": "planner", "password": "scis2024"},
            {"username": "viewer", "password": "scis2024"},
        ]
        self.account = random.choice(accounts)
    
    @task(3)
    def visit_home(self):
        """高频：访问首页（权重3）"""
        self.client.get("/")
    
    @task(2)
    def visit_forecast(self):
        """中频：访问预测页（权重2）"""
        self.client.get("/?nav_page=%F0%9F%93%88+%E9%9C%80%E6%B1%82%E9%A2%84%E6%B5%8B%E5%88%86%E6%9E%90")
    
    @task(2)
    def visit_inventory(self):
        """中频：访问库存页（权重2）"""
        self.client.get("/?nav_page=%F0%9F%93%A6+%E5%BA%93%E5%AD%98%E5%81%A5%E5%BA%B7%E7%9B%91%E6%8E%A7")
    
    @task(1)
    def visit_replenishment(self):
        """低频：访问补货页（权重1）"""
        self.client.get("/?nav_page=%F0%9F%94%84+%E8%A1%A5%E8%B4%A7%E8%AE%A1%E5%88%92%E7%9C%8B%E6%9D%BF")
    
    @task(1)
    def visit_logistics(self):
        """低频：访问物流页（权重1）"""
        self.client.get("/?nav_page=%F0%9F%93%8B+%E9%87%87%E8%B4%AD%E7%89%A9%E6%B5%81%E8%B7%9F%E8%B8%AA")

# 运行命令：locust -f locustfile.py --host=http://47.239.173.51:8501 -u 50 -r 10 -t 60s
# -u 50: 50并发用户
# -r 10: 每秒新增10用户
# -t 60s: 持续60秒
'''

# 在服务器上创建压测脚本
sftp = client.open_sftp()
with sftp.file('/opt/scis/locustfile.py', 'w') as f:
    f.write(locust_script.encode('utf-8'))
print("OK: locustfile.py created")

# 安装 Locust
client.exec_command('cd /opt/scis && /opt/scis/venv/bin/pip install locust -q')
print("OK: Locust installed")

client.close()
print("🎉 Phase 7 压测脚本已部署！")
print("\n运行压测命令：")
print("cd /opt/scis && /opt/scis/venv/bin/locust -f locustfile.py --host=http://47.239.173.51:8501 -u 50 -r 10 -t 60s --headless")
