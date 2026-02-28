from app.models_loader import User, Role
from app.models.base import user_roles
from sqlalchemy import insert, select, update
from sqlalchemy.orm import (
    selectinload,
) 


async def get_all_users(session, is_admin):
    if is_admin:
        result = await session.execute(select(User).where(User.is_active == True))
    else:
        result = await session.execute(
            select(User)
            .join(User.roles)
            .where(User.is_active == True)
            .where(Role.name == "executor")
        )

    return result.scalars().all()


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


async def add_user_role(session, user, roles: list[str]):
    for role in roles:
        result = await session.execute(select(Role).where(Role.name == role))
        user_role = result.scalar_one_or_none()

        if not user_role:
            raise RuntimeError(f"Role {user_role} not found")

        stmt = insert(user_roles).values(user_id=user.id, role_id=user_role.id)
        await session.execute(stmt)


async def update_user_password(session, user, password):
    await session.execute(
        update(User)
        .where(User.id == user.id)
        .values(password_hash=password, must_change_password=False, is_new=False)
    )


