from app.models_loader import User, Role
from app.models.branch import Branch
from app.models.assignment import Assignment
from app.models.client import Client
from app.models.base import user_roles
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import (
    selectinload
)
from app.config.config import ApplicationException
from .common import apply_sorting, order, get_all_and_total


async def owner_exists(session):
    stmt = (
        select(User.id)
        .join(User.roles)
        .where(Role.name == "owner")
        .limit(1)
    )

    owner = await session.scalar(stmt)

    return owner 

async def get_all_users(session, is_admin, query, sorting_rules):
    stmt = select(User).join(User.roles)

    if query.is_active is None or query.is_active is True:
        stmt = stmt.where(User.is_active.is_(True))
    else:
        stmt = stmt.where(User.is_active.is_(False))

    if is_admin and query.role_name:
        stmt = stmt.where(Role.name == query.role_name)

    if not is_admin:
        stmt = stmt.where(Role.name == "executor")

    if query.branch_id is not None:
        stmt = stmt.join(User.branch).where(Branch.id == query.branch_id)

    if query.sort:
        stmt = apply_sorting(stmt=stmt, model=User, sort=query.sort, sorting_rules=sorting_rules)
    else:
        stmt = order(stmt=stmt, model=User)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def get_user_by_email(session, email):
    result = await session.execute(
        select(User).options(selectinload(User.roles)).where(User.email == email)
    )

    user = result.scalar_one_or_none()
    return user


async def get_user_by_id(session, id):
    result = await session.execute(
        select(User)
        .options(selectinload(User.roles))
        .options(selectinload(User.branch))
        .options(selectinload(User.clients))
        .options(selectinload(User.assignments))
        .where(User.id == id)
    )
    user = result.scalar_one_or_none()
    return user


async def add_user(session, data, password, branch_id, password_change):
    user = User(
        branch_id=branch_id,
        name=data.name,
        surname=data.surname,
        position=data.position,
        email=data.email,
        password_hash=password,
        is_active=True,
        must_change_password=password_change,
    )

    session.add(user)
    await session.flush()
    return user


async def add_user_role(session, is_owner: bool, user, new_roles: list[str], is_new=False):
    if not is_new:
        existing_roles = {role.name for role in user.roles}

        if "owner" in existing_roles and "owner" not in new_roles:
            new_roles.append("owner")

        if "owner" not in existing_roles and "owner" in new_roles:
            raise ApplicationException("Роль owner не может быть применена", 400)

    for role in new_roles:
        if role in {"admin"} and not is_owner:
            raise ApplicationException(
                "Только пользователь с ролью owner может назначать роли админам", 403
            )

    result = await session.execute(select(Role).where(Role.name.in_(new_roles)))
    role_objects = result.scalars().all()

    found_role_names = {role.name for role in role_objects}
    missing_roles = set(new_roles) - found_role_names

    if missing_roles:
        raise RuntimeError(f"Roles not found: {missing_roles}")

    await session.execute(
        delete(user_roles).where(user_roles.c.user_id == user.id)
    )
    await session.execute(
        user_roles.insert(),
        [
            {"user_id": user.id, "role_id": role.id}
            for role in role_objects
        ]
    )


async def update_user_password(session, user, password):
    await session.execute(
        update(User)
        .where(User.id == user.id)
        .values(password_hash=password, must_change_password=False)
    )


async def get_user_clients_count(session, user_id):
    stmt = (
        select(func.count(Client.id))
        .where(Client.manager_id == user_id)
        .where(Client.is_archived.is_(False))
    )

    return await session.scalar(stmt) 


async def get_user_assignments_count(session, user_id):
    stmt = (
        select(func.count(Assignment.id))
        .where(Assignment.user_id == user_id)
        .where(Assignment.is_done.is_(False))
    )

    return await session.scalar(stmt) 