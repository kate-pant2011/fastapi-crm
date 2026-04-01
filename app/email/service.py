from .database import get_email_by_id, get_email_by_login, add_email
from .utils import check_smtp_connection, send_email
from app.config.config import ApplicationException
from app.services.common import Access
from app.config.security import encrypt_password, decrypt_password


async def add_email_user(session, items, user_id, roles):
    is_admin = Access(roles).is_admin()

    login = await get_email_by_login(session, items.login)
    if login:
        raise ApplicationException(f"Email {items.login} is already used", 400)
    
    check_smtp_connection(items)

    encrypted_password = encrypt_password(items.password)

    if not items.personal and not is_admin:
        raise ApplicationException("Cannot add puplic emails", 403)
    
    new_email = await add_email(session, items, encrypted_password,  user_id)
    return new_email


async def send_email_service(session, files, email_id, to, cc, subject, body, user_id):
    email = get_email_by_id(session, email_id)
    if not email:
        raise ApplicationException(f"Email not found", 400)
    
    if email.personal and (email.creator_id != user_id):
        raise ApplicationException("cannot use this email", 403)
    
    cc_list = convert_to_brackets(cc)
    to_list = convert_to_brackets(to)
    if not to_list:
        raise ApplicationException("Recipient is required", 400)
    
    password = decrypt_password(email.password)

    await send_email(email, password, to_list, cc_list, subject, body, files)

    return {"status": "sent"}


def convert_to_brackets(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [v.strip() for v in value.split(",") if v.strip()]
