from app.models_loader import Branch
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload


async def get_all_branches(session):
    result = await session.execute(select(Branch).where(Branch.is_archived == False))
    return result.scalars().all()


async def get_branch_by_inn(session, inn: str):
    stmt = select(Branch).where(Branch.inn == inn)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_branch_by_id(session, id: int):
    result = await session.execute(
        select(Branch).options(selectinload(Branch.users)).where(Branch.id == id)
    )
    return result.scalar_one_or_none()


async def add_branch(session, inn: str, company_name: str):
    branch = Branch(
        inn=inn,
        name=company_name,
    )
    session.add(branch)
    await session.flush()
    return branch
