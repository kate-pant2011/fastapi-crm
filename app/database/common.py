from sqlalchemy import select, func
from app.models.base import BaseModel
from app.config.config import ApplicationException
from dataclasses import dataclass


@dataclass
class ORMListResult:
    total: int
    items: list[BaseModel]


async def get_all_and_total(session, stmt, limit, offset):
    count_stmt = select(func.count()).select_from(stmt.distinct().subquery())
    total = await session.scalar(count_stmt)

    stmt = stmt.limit(limit).offset(offset)

    result = await session.execute(stmt)
    items = result.scalars().unique().all()

    return ORMListResult(total=total, items=items)


def apply_sorting(stmt, model: type[BaseModel], sort: str, sorting_rules):
    DESC = False

    if sort.startswith("-"):
        sort = sort.replace("-", "", 1)
        DESC = True

    allowed_fields = sorting_rules.get(sort)

    if not allowed_fields:
        raise ApplicationException(f"Cannot sort by {sort}", 400)

    rule = allowed_fields[0]
    extra_rule = allowed_fields[1] if len(allowed_fields) > 1 else None

    stmt = order(stmt=stmt, model=model, rule=rule, extra_rule=extra_rule, DESC=DESC)
    return stmt


def order(stmt, model: type[BaseModel], rule=None, extra_rule=None, DESC=False):
    if not rule:
        stmt = stmt.order_by(model.created_at.desc(), model.id.desc())
        return stmt

    field = getattr(model, rule)

    if extra_rule:
        extra_field = getattr(model, extra_rule)

        if DESC:
            stmt = stmt.order_by(field.desc(), extra_field, model.id.desc())
        else:
            stmt = stmt.order_by(field, extra_field, model.id)

    else:
        if DESC:
            stmt = stmt.order_by(field.desc(), model.id.desc())
        else:
            stmt = stmt.order_by(field, model.id)

    return stmt
