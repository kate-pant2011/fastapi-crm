import smtplib
from email.message import EmailMessage
from app.config.config import ApplicationException


def check_smtp_connection(smtp_config):
    try: 
        smtp = smtplib.SMTP(smtp_config.server, smtp_config.port)
        smtp.starttls()
        smtp.login(smtp_config.login, smtp_config.password)

    except smtplib.SMTPAuthenticationError:
        raise ApplicationException("Invalid SMTP credentials", 400)

    except Exception:
        raise

    finally:
        if smtp:
            smtp.quit()


async def send_email(smtp_config, password, to, cc, subject, body, files):
    smtp = None
    try:
        if smtp_config.port == 465:
            smtp = smtplib.SMTP_SSL(smtp_config.server, smtp_config.port)
        else:
            smtp = smtplib.SMTP(smtp_config.server, smtp_config.port)
            smtp.starttls()

        smtp.login(smtp_config.login, password)

        msg = EmailMessage()
        msg["From"] = smtp_config.login
        msg["To"] = ", ".join(to)
        if cc:
            msg["Cc"] = ", ".join(cc) 
        msg["Subject"] = subject or ""
        msg.set_content(body or "")

        if files:
            for file in files:
                content = await file.read()
                msg.add_attachment(
                    content,
                    maintype="application",
                    subtype="octet-stream",
                    filename=file.filename
                )

        smtp.send_message(msg,to_addrs=to + cc)

    except smtplib.SMTPAuthenticationError:
        raise ApplicationException("Invalid SMTP credentials", 400)
    
    except smtplib.SMTPRecipientsRefused:
        raise ApplicationException("Invalid recipient email", 400)

    finally:
        if smtp:
            smtp.quit()