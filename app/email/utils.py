import smtplib
from email.message import EmailMessage
from app.config.config import ApplicationException
from dataclasses import dataclass

@dataclass
class EmailDTO:
    server: str
    port: int

KNOWN_PROVIDERS = {
    "gmail.com": {
        "smtp": "smtp.gmail.com",
        "port": 465,
    },
    "yandex.ru": {
        "smtp": "smtp.yandex.ru",
        "port": 465,
    },
    "mail.ru": {
        "smtp": "smtp.mail.ru",
        "port": 465,
    },
    "rambler.ru": {
            "smtp": "mail.rambler.ru",
            "port": 465,
    },
    "outlook.com": {
        "smtp": "smtp.office365.com",
        "port": 587
    }
}

def define_host_and_port(config):
    if config.port and config.server:
        return EmailDTO(server=config.server, port=config.port)
    
    if config.server or config.port:
        raise ApplicationException(
            "Both server and port must be provided", 400
    )
    try: 
        domain = config.login.split("@")[1]

    except IndexError:
        raise ApplicationException(
            "Invalid email login",
            400
        )
    provider = KNOWN_PROVIDERS[domain]
    if not provider:
        raise ApplicationException("Unknown email provider. Specify SMTP server and port manually", 400)

    server = provider.get("smtp") 
    port = provider.get("port")
    return  EmailDTO(server=server, port=port)


def check_smtp_connection(server, port, login, password):
    smtp = None
    try:
        if port == 465:
            smtp = smtplib.SMTP_SSL(server, port)
        else:
            smtp = smtplib.SMTP(server, port)
            smtp.starttls()
            
        smtp.login(login, password)

    except smtplib.SMTPAuthenticationError:
        raise ApplicationException("Invalid SMTP credentials", 400)

    except Exception:
        raise

    finally:
        if smtp:
            smtp.quit()


async def send_email(smtp_config, password, to, cc, bcc, subject, body, files):
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
                if file.path:
                    with open(file.path, "rb") as f:
                        content = f.read()
                else:
                    content = file.content

                if not file.filename:
                    continue
                if not content:
                    continue
                
                msg.add_attachment(
                    content,
                    maintype="application",
                    subtype="octet-stream",
                    filename=file.filename
                )

        all_recipients = to + cc + bcc
        smtp.send_message(msg,to_addrs=all_recipients)

    except smtplib.SMTPAuthenticationError:
        raise ApplicationException("Invalid SMTP credentials", 400)
    
    except smtplib.SMTPRecipientsRefused:
        raise ApplicationException("Invalid recipient email", 400)

    finally:
        if smtp:
            smtp.quit()