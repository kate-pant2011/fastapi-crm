from sqlalchemy import select
from app.database.common import apply_sorting,  get_all_and_total, order
from app.models.email_log import EmailLog
from app.config.config import ApplicationException

async def add_email_log(session, user_id, login, to, cc, bcc, subject, body, files_data):
    email_log =EmailLog(
        user_id = user_id,
        from_email = login,
        to = to,
        cc = cc,
        bcc = bcc,
        subject = subject,
        body = body,
        files_data = files_data,
    )

    session.add(email_log)
    await session.flush()
    return email_log


async def get_filtered_email_logs(session, is_admin, query, sorting_rules, user_id):
    stmt = select(EmailLog)

    if not is_admin or (is_admin and query.scope == "mine"):
        stmt = stmt.where(EmailLog.user_id == user_id)

    if query.user_id is not None:
        if not is_admin:
            raise ApplicationException("Not enough permissions", 403)
        
        stmt = stmt.where(EmailLog.user_id == query.user_id)

    if query.from_email is not None:
        stmt = stmt.where(EmailLog.from_email == query.from_email)

    if query.to_email is not None:
        stmt = stmt.where(EmailLog.to.any(query.to_email.lower())) 

    if query.status is not None:
        stmt = stmt.where(EmailLog.status == query.status)

    if query.sort:
        stmt = apply_sorting(stmt=stmt, model=EmailLog, sort=query.sort, sorting_rules=sorting_rules)
    else:
        stmt = order(stmt=stmt, model=EmailLog)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def get_email_log_by_id(session, is_admin, user_id, email_log_id):
    stmt = (
        select(EmailLog)
        .where(EmailLog.id == email_log_id)
    )
    if not is_admin:
        stmt = stmt.where(EmailLog.user_id == user_id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()