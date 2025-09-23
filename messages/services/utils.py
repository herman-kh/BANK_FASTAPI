import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import settings
import logging
from email.message import EmailMessage




async def send_email(subject, body, to_email, from_email, password) -> bool:
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        msg.set_content(body)

        async with aiosmtplib.SMTP(hostname='smtp.gmail.com', port=465, use_tls=True) as smtp:
            await smtp.login(from_email, password)
            await smtp.send_message(msg)

        logging.info("Письмо отправлено!")
        return True
    except Exception as e:
        logging.info(f'Ошибка: {e}')
        return False
    
