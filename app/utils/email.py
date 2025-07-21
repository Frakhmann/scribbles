import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD



def send_confirmation_email(to_email, confirmation_link):
    subject = 'Активация аккаунта Scribbles'
    body = f'Здравствуйте! Перейдите по ссылке для активации аккаунта: {confirmation_link}'

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True, 'Письмо отправлено!'
    except Exception as e:
        return False, str(e)

