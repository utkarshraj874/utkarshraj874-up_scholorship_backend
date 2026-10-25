import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to: str, subject: str, body: str):
    """Send an email using SMTP.
    If SMTP environment variables are not set, fallback to printing the email content.
    Expected env vars:
        SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_TLS (optional, "true"/"false")
    """
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    use_tls = os.getenv('SMTP_TLS', 'true').lower() == 'true'

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        # Fallback: print to console for development/testing
        print('--- Email Stub ---')
        print(f'To: {to}')
        print(f'Subject: {subject}')
        print('Body:')
        print(body)
        print('--- End Email Stub ---')
        return

    # Construct message
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            if use_tls:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print('Email sent successfully')
    except Exception as e:
        print(f'Failed to send email: {e}')
        # Still fallback to console output for visibility
        print('--- Email Fallback Output ---')
        print(f'To: {to}\nSubject: {subject}\n{body}\n--- End ---')
