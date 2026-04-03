import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


def send_verification_email(recipient_email, username, verification_link):
    """Send verification email to user"""

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("⚠ Warning: Email credentials not configured. Email not sent.")
        print(f"Verification link: {verification_link}")
        return False

    try:
        # Create email
        message = MIMEMultipart("alternative")
        message["Subject"] = "Verify Your DiaPredict Account"
        message["From"] = SENDER_EMAIL
        message["To"] = recipient_email

        # HTML content
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                <h1 style="margin: 0;">🏥 DiaPredict</h1>
                <p style="margin: 10px 0 0 0;">Early Diabetes Detection System</p>
              </div>

              <h2 style="color: #667eea;">Hello {username}! 👋</h2>
              <p>Thank you for registering with DiaPredict. To complete your account setup, please verify your email address by clicking the button below:</p>

              <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                  ✓ Verify Email Address
                </a>
              </div>

              <p style="color: #666; font-size: 14px;">Or copy and paste this link in your browser:</p>
              <p style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 12px;">
                {verification_link}
              </p>

              <p style="color: #666; font-size: 14px; margin-top: 20px;">
                <strong>This link will expire in 24 hours.</strong>
              </p>

              <p style="color: #999; font-size: 12px; border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px;">
                If you didn't create this account, please ignore this email.
              </p>

              <p style="color: #999; font-size: 12px;">
                © 2024 DiaPredict. All rights reserved.
              </p>
            </div>
          </body>
        </html>
        """

        part = MIMEText(html, "html")
        message.attach(part)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())

        print(f"✓ Verification email sent to {recipient_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("✗ SMTP Authentication Error: Check email credentials")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False


def send_welcome_email(recipient_email, username):
    """Send welcome email after account verification"""

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("⚠ Warning: Email credentials not configured.")
        return False

    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Welcome to DiaPredict! 🎉"
        message["From"] = SENDER_EMAIL
        message["To"] = recipient_email

        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                <h1 style="margin: 0;">🏥 DiaPredict</h1>
                <p style="margin: 10px 0 0 0;">Early Diabetes Detection System</p>
              </div>

              <h2 style="color: #667eea;">Welcome to DiaPredict, {username}! 🎉</h2>
              <p>Your account has been successfully verified. You can now start using DiaPredict to monitor your health and detect early signs of diabetes.</p>

              <h3 style="color: #667eea;">What You Can Do:</h3>
              <ul>
                <li>📊 Take personalized diabetes risk assessments</li>
                <li>📈 Track your health metrics over time</li>
                <li>📉 Visualize your test results with interactive charts</li>
                <li>💾 View your complete prediction history</li>
                <li>📋 Get personalized health recommendations</li>
              </ul>

              <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5000/dashboard" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                  Go to Dashboard
                </a>
              </div>

              <p style="color: #999; font-size: 12px; border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px;">
                © 2024 DiaPredict. All rights reserved.
              </p>
            </div>
          </body>
        </html>
        """

        part = MIMEText(html, "html")
        message.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())

        print(f"✓ Welcome email sent to {recipient_email}")
        return True

    except Exception as e:
        print(f"✗ Error sending welcome email: {e}")
        return False
