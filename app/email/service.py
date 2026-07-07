from .database import get_email_by_id, get_email_by_login, add_email, get_all_emails
from app.database.user import get_user_by_id
from .utils import check_smtp_connection, send_email, define_host_and_port
from app.database.email_log import add_email_log
from app.models.email_log import EmailLogStatus
from app.config.config import ApplicationException
from app.services.common import Access
from app.config.security import encrypt_password, decrypt_password
from app.services.common import Access
from app.file_handler import FileHandler
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

async def get_email_list(session, limit, offset, user_id, roles, scope):
    is_admin = Access(roles).is_admin()

    emails = await get_all_emails(session, limit, offset, is_admin, user_id, scope)

    return {
        "items": emails.items,
        "total": emails.total,
        "limit": limit,
        "offset": offset,
    }


async def get_email(session, email_id):
    email = await get_email_by_id(session, email_id)

    if not email:
        raise ApplicationException(f"Email not found", 404)

    return email


async def change_email(session, item, email_id, user_id):
    email = await get_email(session, email_id)     

    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():
        if name == "owner_id" and value is not None:
            user = await get_user_by_id(session, value)

            if user is None:  
                    raise ApplicationException("User not found", 404)
            
            email.owner_id = value

        else:
            if email.creator_id != user_id:
                raise ApplicationException("Only creator can update email settings", 403)

            if name == "password":
                value = encrypt_password(value)

            setattr(email, name, value)

    if any(field in update_data for field in ["login", "password", "server", "port"]):
        check_smtp_connection(
            email.server,
            email.port,
            email.login,
            decrypt_password(email.password)
        )

    return email


async def delete_email(session, email_id, user_id, roles):
    is_owner = Access(roles).is_owner()
    email = await get_email(session, email_id)

    if email.creator_id != user_id and not is_owner:
        raise ApplicationException(f"Only creator or owner can delete account", 403)  

    await session.delete(email)

    return {"status": "deleted"}


async def add_email_user(session, items, user_id):
    login = await get_email_by_login(session, items.login)
    if login:
        raise ApplicationException(f"Email {items.login} is already used", 400)

    if items.assigned_user_id is not None:
        user = await get_user_by_id(session, items.assigned_user_id)
        if not user:
            raise ApplicationException(f"User with id {items.assigned_user_id} not found", 404)

    smtp = define_host_and_port(items)
    check_smtp_connection(smtp.server, smtp.port, items.login, items.password)

    encrypted_password = encrypt_password(items.password)
    
    new_email = await add_email(session, items, smtp.server, smtp.port, encrypted_password, user_id)

    return new_email


@dataclass
class FileValidateDTO:
    filename: str
    mime_type: str
    size: int
    content: bytes | None = None
    path: str | None = None

async def validate_fastapi_file(files):
    validated_files = []
    handler = FileHandler()

    if files:
        for file in files:
            data = await handler.validate_file(file)
            data = FileValidateDTO(
                filename = data.get("filename"),
                mime_type= data.get("mime_type"),
                size = data.get("size"),
                path = None,
                content = data.get("content")
            )
            validated_files.append(data)

    return validated_files


async def send_email_service(session, files, email_id, to, cc, bcc, subject, body, user_id):
    email = await get_email_by_id(session, email_id)
    if not email:
        raise ApplicationException(f"Email not found", 400)
    
    if email.owner_id is not None:
        if email.owner_id != user_id:
            raise ApplicationException("Cannot use this email", 403)
    
    cc_list = convert_to_brackets(cc)
    bcc_list = convert_to_brackets(bcc)
    to_list = convert_to_brackets(to)
    if not to_list:
        raise ApplicationException("Recipient is required", 400)
    
    password = decrypt_password(email.password)

    files_info = []

    for f in files:
        data = {
            "filename": f.filename or "unknown",
            "size": f.size,
            "mime_type": f.mime_type,
        }
        files_info.append(data)

    email_log = await add_email_log(
        session, user_id, 
        email.login, to_list, 
        cc_list, bcc_list,
        subject, body, files_info
    )

    try:
        await send_email(email, password, to_list, cc_list, bcc_list, subject, body, files)
        email_log.status = EmailLogStatus.SENT
        email_log.sent_at = datetime.utcnow()

    except Exception as e:
        email_log.status = EmailLogStatus.FAILED
        email_log.error_message = str(e)
        logger.exception("smtp send failed")
        return {"status": "failed"}

    finally:
        await session.commit()

    return {"status": "sent"}


def convert_to_brackets(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [v.strip() for v in value.split(",") if v.strip()]

