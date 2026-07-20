import paramiko
import io

# SSH连接
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('47.239.173.51', username='root', password='JWYjys5210@', timeout=30)

# 读取完整文件
sftp = client.open_sftp()
with sftp.file('/opt/scis/streamlit_app.py', 'r') as f:
    content = f.read().decode('utf-8')

# ========================================
# 替换1: page_guide 标题区域
# ========================================
old_guide_title = '''    st.title("📘 使用指南")
    st.markdown("<p style='color: #6B7280;'>系统操作手册与流程说明</p>", unsafe_allow_html=True)
    st.markdown("---")'''

new_guide_title = '''    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center;
                background: white; border-radius: 12px; padding: 20px 24px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #457B9D;
                margin-bottom: 20px;">
        <div>
            <h1 style="color: #1B4965; margin: 0; font-size: 24px; font-weight: 600;">📘 使用指南</h1>
            <p style="color: #6B7280; margin: 4px 0 0 0; font-size: 14px;">系统操作手册与流程说明</p>
        </div>
        <div style="font-size: 32px; opacity: 0.3;">📘</div>
    </div>
    """, unsafe_allow_html=True)'''

if old_guide_title in content:
    content = content.replace(old_guide_title, new_guide_title, 1)
    print("✅ page_guide 标题替换成功")
else:
    print("❌ page_guide 标题未找到，尝试备选匹配...")

# ========================================
# 替换2: page_ops_center 标题区域
# ========================================
old_ops_title = '''    st.title("⚙️ 运维中心")
    st.markdown("<p style='color: #6B7280;'>问题反馈提交与系统工单管理</p>", unsafe_allow_html=True)
    st.markdown("---")'''

new_ops_title = '''    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center;
                background: white; border-radius: 12px; padding: 20px 24px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #F4A261;
                margin-bottom: 20px;">
        <div>
            <h1 style="color: #1B4965; margin: 0; font-size: 24px; font-weight: 600;">⚙️ 运维中心</h1>
            <p style="color: #6B7280; margin: 4px 0 0 0; font-size: 14px;">问题反馈提交与系统工单管理</p>
        </div>
        <div style="font-size: 32px; opacity: 0.3;">⚙️</div>
    </div>
    """, unsafe_allow_html=True)'''

if old_ops_title in content:
    content = content.replace(old_ops_title, new_ops_title, 1)
    print("✅ page_ops_center 标题替换成功")
else:
    print("❌ page_ops_center 标题未找到")

# 写回文件
with sftp.file('/opt/scis/streamlit_app.py', 'w') as f:
    f.write(content.encode('utf-8'))

sftp.close()
client.close()
print("\n🚀 文件已更新")
