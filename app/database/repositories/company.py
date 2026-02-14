from app.models_loader import Company
from sqlalchemy import select

async def get_company_by_inn(session, inn: int):
    stmt = select(Company).where(Company.inn == inn)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create_company(session, inn: int, company_name: str):
    company = Company(
        inn=inn,
        name=company_name,
    )
    session.add(company)
    await session.flush()
    return company

