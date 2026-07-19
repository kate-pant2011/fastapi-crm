import secrets
import string
import logging
from app.database.user import (
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    add_user,
    add_user_role,
    get_user_assignments_count,
    get_user_clients_count
)
from app.database.branch import get_branch_by_id
from app.config.config import ApplicationException
from app.config.security import hash_password
from app.schemas.common import to_schema, BaseShortResponse
from app.schemas.user import UserItem
from .common import Access, ROLES
from app.email.templates import send_invitation_email


logger = logging.getLogger(__name__)

async def build_user_item(session, user):
    clients_count = await get_user_clients_count(session, user.id)
    assignments_count = await get_user_assignments_count(session, user.id)

    return {
        "name": user.name,
        "surname": user.surname,
        "position": user.position,
        "email": user.email,
        "branch": to_schema(BaseShortResponse, user.branch),
        "roles": [to_schema(BaseShortResponse, role) for role in user.roles],
        "clients_count": clients_count,
        "assignments_count": assignments_count,
    }

sorting_rules = {"name": ("name", "surname"), "surname": ("surname", "name")}

async def get_user_list(session, roles, query):
    is_admin = Access(roles).is_admin()

    if query.role_name is not None and query.role_name not in ROLES:
        raise ApplicationException(
            f"Role named '{query.role_name}' does not exist", 400
        )

    users = await get_all_users(session, is_admin, query, sorting_rules)

    return {
        "items": users.items or [],
        "total": users.total,
        "limit": query.limit,
        "offset": query.offset,
    }


async def get_user(session, user_id, roles):
    user = await get_user_by_id(session, user_id)
    if not user:
        raise ApplicationException("User Not found", 404)

    if not user.is_active:
        raise ApplicationException("User is archived", 400, {"id": user.id})

    target_roles = list({role.name for role in user.roles})

    if not target_roles:
        raise ApplicationException("Roles Not found", 404)

    is_admin = Access(roles).is_admin()
    is_executor = Access(target_roles).is_executor()

    if not is_admin and not is_executor:
        raise ApplicationException(
            f"Cannot access user with {target_roles} status", 403
        )

    user_item =  await build_user_item(session, user)
    return user_item


async def get_user_me(session, user_id):
    user = await get_user_by_id(session, user_id)
    if not user:
        raise ApplicationException("User Not found", 404)

    if not user.is_active:
        raise ApplicationException("User is archived", 400, {"id": user.id})

    user_item =  await build_user_item(session, user)
    return user_item


async def change_user(session, roles, user_id, item):
    is_owner = Access(roles).is_owner()

    user = await get_user_by_id(session, user_id)
    if not user:
        raise ApplicationException("User Not found", 404)

    if not user.is_active:
        raise ApplicationException(f"A user '{user.name}' is archived", 400, {"id": user.id})

    update_data = item.model_dump(exclude_unset=True)

    if "branch_id" in update_data:
        branch = await get_branch_by_id(session, update_data.get("branch_id"))
        if not branch:
            raise ApplicationException("Company Not found", 404)

        if branch.is_archived:
            raise ApplicationException(
                f"A company with INN {branch.inn} is archived", 400, {"id": branch.id}
            )

    if "role" in update_data:
        new_roles = update_data.get("role")

        await add_user_role(
            session=session,
            is_owner=is_owner,
            user=user,
            new_roles=new_roles,
        )

    for name, value in update_data.items():
        if name == "role":
            continue

        setattr(user, name, value)

    return to_schema(BaseShortResponse, user)


async def create_user(session, roles, data):
    is_owner = Access(roles).is_owner()

    user = await get_user_by_email(session, data.email)
    if user:
        if not user.is_active:
            raise ApplicationException("User is archived", 400, {"id": user.id})

        raise ApplicationException(f"Email {data.email} is already used", 400)

    branch = await get_branch_by_id(session, data.branch_id)
    if not branch:
        raise ApplicationException("Company Not found", 404)

    if branch.is_archived:
        raise ApplicationException(f"A company with INN {branch.inn} is archived", 400, {"id": branch.id})

    if "owner" in data.roles:
        raise ApplicationException("Role owner cannot be applied", 400)
    
    password = generate_password()
    hashed_password = hash_password(password)

    new_user = await add_user(
        session, data, hashed_password, branch.id, password_change=True
    )

    await add_user_role(session, is_owner, new_user, data.roles, True)

    try:
        await send_invitation_email(
            to=data.email, password=password
        )
    except Exception as e:
        logger.exception(f"SMTP error - Failed to send invitation email")


    return {"name": new_user.name, "user_id": new_user.id}


def generate_password():
    symbols = string.ascii_letters + string.digits
    password = "".join(secrets.choice(symbols) for i in range(10))
    return password


async def archive_user(session, user_id):
    user = await get_user_by_id(session, user_id)

    if not user:
        raise ApplicationException("User Not found", 404)

    if not user.is_active:
        raise ApplicationException("User is already archived", 400)

    user.is_active = False
    return user


async def restore_user(session, user_id):
    user = await get_user_by_id(session, user_id)

    if not user:
        raise ApplicationException("User Not found", 404)

    if user.is_active:
        raise ApplicationException("User is already active", 400)

    user.is_active = True
    return user


async def resend_signup_invitation(session, user_id):
    user = await get_user_by_id(session, user_id)

    if not user:
        raise ApplicationException("User Not found", 404)

    if not user.is_active:
        raise ApplicationException(
            f"User '{user.name}' is archived", 400, {"id": user.id}
        )
    
    if not user.must_change_password:
        raise ApplicationException(
            f"user '{user.name}' has already completed registration", 400
        )

    password = generate_password()
    hashed_password = hash_password(password)

    try:
        await send_invitation_email(
            session=session, to=user.email, password=password
        )
    except Exception:
        logger.exception(f"SMTP error - Failed to send invitation email")

    user.password_hash = hashed_password

    return {"name": user.name, "user_id": user.id}  

