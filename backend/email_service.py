"""
email_service.py - Email notifications
"""

import os
from typing import List, Tuple
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv('.env.production')

class EmailService:
    """Send emails via SMTP (Gmail or custom)"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@peterai.net")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.enabled = bool(self.sender_password)
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> Tuple[bool, str]:
        """Send email"""
        
        if not self.enabled:
            return True, "[MOCK] Email sent (SMTP not configured)"
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = to_email
            
            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, msg.as_string())
            
            return True, "Email sent successfully"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"
    
    # ===== EMAIL TEMPLATES =====
    
    def welcome_email(self, user_email: str, username: str) -> Tuple[bool, str]:
        """Welcome email for new user"""
        subject = "Selamat Datang di PETER AI! 🎉"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #d4af37;">PETER AI</h1>
                    <h2>Selamat Datang, {username}! 👋</h2>
                    <p>Akun Anda telah berhasil dibuat di PETER AI.</p>
                    <p>Mulai dengan tier <strong>Free</strong> dan upgrade kapan saja.</p>
                    <a href="https://peterai.net" style="background-color: #d4af37; color: #1a1a1a; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Masuk ke Dashboard
                    </a>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">© 2026 PETER AI. Semua hak dilindungi.</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_body)
    
    def workspace_invite(self, to_email: str, inviter_name: str, workspace_name: str, invite_link: str) -> Tuple[bool, str]:
        """Workspace invitation email"""
        subject = f"{inviter_name} mengundang Anda ke {workspace_name}"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 600px;">
                    <h2>{inviter_name} mengundang Anda! 👋</h2>
                    <p>Bergabunglah dengan workspace <strong>{workspace_name}</strong> di PETER AI.</p>
                    <a href="{invite_link}" style="background-color: #d4af37; color: #1a1a1a; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Terima Undangan
                    </a>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_body)
    
    def usage_alert(self, to_email: str, username: str, usage_percent: int) -> Tuple[bool, str]:
        """Usage limit alert"""
        subject = f"⚠️ Usage Alert: {usage_percent}% dari quota Anda"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="background-color: white; padding: 30px; border-radius: 10px;">
                    <h2>Usage Alert 🔔</h2>
                    <p>Halo {username},</p>
                    <p>Anda sudah menggunakan <strong>{usage_percent}%</strong> dari quota bulan ini.</p>
                    <p>Upgrade plan Anda untuk akses unlimited.</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_body)

# Global instance
_email_service: EmailService = None

def get_email_service() -> EmailService:
    """Get email service"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

def init_email_service() -> EmailService:
    """Initialize email service"""
    global _email_service
    _email_service = EmailService()
    return _email_service