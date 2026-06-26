from app.models_loader import Branch
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .common import apply_sorting, order, get_all_and_total


async def get_all_branches(session, query, sorting_rules):
    stmt = select(Branch).where(Branch.is_archived.is_(False))

    if not query.sort:
        stmt = order(stmt=stmt, model=Branch)

    else:
        stmt = apply_sorting(stmt=stmt, model=Branch, sort=query.sort, sorting_rules=sorting_rules)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def get_branch_by_inn(session, inn: str):
    stmt = select(Branch).where(Branch.inn == inn)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_branch_by_id(session, id: int):
    result = await session.execute(
        select(Branch).options(selectinload(Branch.users)).where(Branch.id == id)
    )
    return result.scalar_one_or_none()


async def get_branch_by_id_with_stamp(session, id: int):
    result = await session.execute(
        select(Branch).options(selectinload(Branch.stamp_file)).where(Branch.id == id)
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
