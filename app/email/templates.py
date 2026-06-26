from app.config.config import ApplicationException, settings
from app.email.utils import send_email
from dataclasses import dataclass

@dataclass
class EmailConfigDTO:
    server: str
    port: int
    login: str

smtp_config = EmailConfigDTO(
    port = settings.SMTP_PORT,
    server = settings.SMTP_HOST,
    login = settings.EMAIL_USER
)

async def send_invitation_email(to, password):

    await send_email(
        smtp_config=smtp_config,
        password=settings.EMAIL_PASSWORD,
        to=[to], 
        cc=[], 
        bcc=[], 
        subject="Завершение авторизации пользователя", 
        body=(
            f"Временный пароль для входа в учетную запись: {password}\n\n"
            "Для окончания регистрации необходимо сменить временный пароль после первой авторизации!\n\n"
            "С уважением,\nкоманда CRM"
        ), 
        files=None
    )



async def send_complete_registration_email(to, reset_token):

    link = f"http://127.0.0.1:8000/reset-password?token={reset_token}"

    await send_email(
        smtp_config=smtp_config,
        password=settings.EMAIL_PASSWORD,
        to=[to], 
        cc=[], 
        bcc=[], 
        subject="Запрос на смену пароля", 
        body=(
            f"Для смены пароля пройдите по ссылке: {link}\n\n"
            "Если вы не запрашивали смену пароля,"
            "не переходите по ссылкам из уведомления и не сообщайте никому коды из СМС." 
            "Скорее всего, кто-то ошибся адресом почты или пытается получить доступ к вашему аккаунту.\n\n"
            "С уважением,\nкоманда CRM"
        ), 
        files=None
    )

async def send_suspicios_login_attempt_caution(to, reason):
    await send_email(
        smtp_config=smtp_config,
        password=settings.EMAIL_PASSWORD,
        to=[to], 
        cc=[], 
        bcc=[], 
        subject="Попытка входа в аккаунт", 
        body=(
            f"Была осуществлена попытка входа в Ваш аккаунт!\n\nСпособ: {reason}\n\n"
            "С уважением,\nкоманда CRM"
        ), 
        files=None
    )
