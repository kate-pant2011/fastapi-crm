from app.models_loader import User, Role
from app.models.base import user_roles
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload # Если AsyncSession, нужно обратиться к relationship, иначе НАДО ловить MissingGreenlet


async def get_user_by_email(session, email):
    result = await session.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.email == email)
    )

    user = result.scalar_one_or_none()
    return user

async def get_user_by_id(session, id):
    stmt = select(User).options(selectinload(User.roles)).where(User.id == id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_user(session, login, password, name, surname, position, new_company):
    user = User(
        branch=new_company,
        name=name,
        surname=surname,
        position=position, 
        email=login, 
        password_hash=password, 
        is_active=True
    )

    session.add(user)
    await session.flush()
    return user


async def add_user_role(session, user):
    result = await session.execute(select(Role).where(Role.name == "owner"))
    role = result.scalar_one_or_none()

    if not role:
        raise RuntimeError("Role 'owner' not found")
    
    stmt = insert(user_roles).values(
        user_id=user.id,
        role_id=role.id
    )
    await session.execute(stmt) 
