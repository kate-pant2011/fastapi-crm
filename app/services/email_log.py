from app.database.email_log import (
    get_filtered_email_logs,
    get_email_log_by_id,

)
from app.config.config import ApplicationException
from .common import Access

sorting_rules = {"status": ("status","created_at")}

async def get_email_log_list(session, roles, user_id, query):
    access = Access(roles)
    is_admin = access.is_admin()

    email_logs = await get_filtered_email_logs(
        session=session, is_admin=is_admin, query=query, sorting_rules=sorting_rules, user_id=user_id
    )

    if not email_logs:
        raise ApplicationException("Запись сообщения не найдена", 404)

    return {
        "items": email_logs.items,
        "total": email_logs.total,
        "limit": query.limit,
        "offset": query.offset,
    }


async def get_email_log(session, roles, user_id, email_log_id):
    access = Access(roles)
    is_admin = access.is_admin()

    email_log = await get_email_log_by_id(session, is_admin, user_id, email_log_id)
    if not email_log:
        raise ApplicationException("Запись сообщения не найдена", 404)

    return email_log