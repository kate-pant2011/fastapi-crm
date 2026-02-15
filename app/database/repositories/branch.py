from app.models_loader import Branch
from sqlalchemy import select

async def get_company_by_inn(session, inn: int):
    stmt = select(Branch).where(Branch.inn == inn)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create_company(session, inn: int, company_name: str):
    branch = Branch(
        inn=inn,
        name=company_name,
        main_branch=True
    )
    session.add(branch)
    await session.flush()
    return branch

