from app.models_loader import Branch
from sqlalchemy import select, update

async def get_all_branches(session):
    result = await session.execute(select(Branch))
    return result.scalars().all()

async def get_company_by_inn(session, inn: str):
    stmt = select(Branch).where(Branch.inn == inn)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_company_by_id(session, id: int):
    result = await session.execute(
        select(Branch)
        .where(Branch.id == id)
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

async def archive_branch(session, inn: str):
    await session.execute(
        update(Branch)
        .where(Branch.inn == inn)
        .values(is_deleted=True)
    )

async def activate_branch(session, branch):
    await session.execute(
        update(Branch)
        .where(Branch.inn == branch.inn)
        .values(is_deleted=False)
    )
    
    
    