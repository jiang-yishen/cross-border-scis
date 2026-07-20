import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 163邮箱SMTP配置
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
SENDER_EMAIL = "15143585991@163.com"
SENDER_PASSWORD = "NYm2PX3X4sD9iuuQ"  # SMTP授权码
RECEIVER_EMAIL = "15143585991@163.com"

def send_feedback_email(feedback_data: dict) -> bool:
    """发送用户问题反馈邮件通知
    
    Args:
        feedback_data: 反馈数据字典，包含 type, description, contact 等字段
    
    Returns:
        bool: 发送成功返回True，失败返回False
    """
    try:
        # 创建邮件内容
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 SCIS系统反馈 - {feedback_data.get('type', '未分类')}"
        msg["From"] = f"SCIS系统 <{SENDER_EMAIL}>"
        msg["To"] = RECEIVER_EMAIL
        
        # 邮件正文（HTML格式）
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: #FFF8E7; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h2 style="color: #5D4037; margin-top: 0;">🐾 跨境海外仓供应链智能决策系统</h2>
                <p style="color: #8D6E63; font-size: 14px;">用户问题反馈通知</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h3 style="color: #1B4965; margin-top: 0;">📋 反馈详情</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee; width: 120px;"><b>反馈类型</b></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">{feedback_data.get('type', '未填写')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><b>详细描述</b></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">{feedback_data.get('description', '未填写')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><b>联系方式</b></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">{feedback_data.get('contact', '未填写')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><b>提交时间</b></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">{feedback_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background: #E8F5E9; padding: 15px; border-radius: 8px; border-left: 4px solid #2A9D8F;">
                <p style="margin: 0; color: #1B5E20;"><b>💡 处理建议：</b></p>
                <p style="margin: 5px 0 0 0; color: #2E7D32; font-size: 13px;">
                    1. 登录系统运维中心查看完整工单详情<br>
                    2. 根据优先级安排处理<br>
                    3. 处理完成后及时更新工单状态
                </p>
            </div>
            
            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 12px;">
                <p>此邮件由 SCIS 系统自动发送 | 跨境海外仓供应链智能决策系统</p>
                <p>🐈 让库存管理更轻松，让决策更智能 🐈</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        
        # 连接SMTP服务器并发送
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        
        print(f"✅ 邮件发送成功: {feedback_data.get('type', '未分类')}")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")
        return False


def send_system_notification(subject: str, content: str) -> bool:
    """发送系统通知邮件（通用）
    
    Args:
        subject: 邮件主题
        content: 邮件正文（纯文本）
    
    Returns:
        bool: 发送成功返回True
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔔 SCIS系统通知 - {subject}"
        msg["From"] = f"SCIS系统 <{SENDER_EMAIL}>"
        msg["To"] = RECEIVER_EMAIL
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: #FFF8E7; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h2 style="color: #5D4037; margin-top: 0;">🐾 SCIS系统通知</h2>
            </div>
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px;">
                <p>{content}</p>
            </div>
            <div style="margin-top: 20px; text-align: center; color: #999; font-size: 12px;">
                <p>此邮件由 SCIS 系统自动发送</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        
        print(f"✅ 系统通知邮件发送成功: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ 系统通知邮件发送失败: {str(e)}")
        return False
