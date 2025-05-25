# app/services/email.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from typing import Optional

async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html: bool = False
) -> bool:
    """
    Sends an email using SMTP settings from config.
    Returns True on success, False otherwise.
    """
    if not settings.SMTP_HOST or not settings.SMTP_PORT or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"EMAIL SERVICE: SMTP settings not fully configured. Cannot send email to {to_email}. Subject: {subject}")
        print(f"Email Body:\n{body}")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    if html:
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        print(f"EMAIL SERVICE: Successfully sent email to {to_email} with subject: {subject}")
        return True
    except Exception as e:
        print(f"EMAIL SERVICE ERROR: Could not send email to {to_email}. Subject: {subject}. Error: {e}")
        return False

# Helper functions for specific email types
async def send_verification_email(email: str, username: str, verification_url: str):
    subject = "Verify Your Email for Journaling App"
    body = f"""
    Hi {username},

    Thank you for registering with our Journaling App!
    Please click on the link below to verify your email address:

    {verification_url}

    This link will expire in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES} minutes.

    If you did not register for an account, please ignore this email.

    Best regards,
    The Journaling App Team
    """
    await send_email(email, subject, body)

async def send_password_reset_email(email: str, username: str, reset_url: str):
    subject = "Password Reset Request for Journaling App"
    body = f"""
    Hi {username},

    We received a request to reset your password for your Journaling App account.
    Please click on the link below to reset your password:

    {reset_url}

    This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.

    If you did not request a password reset, please ignore this email.

    Best regards,
    The Journaling App Team
    """
    await send_email(email, subject, body)