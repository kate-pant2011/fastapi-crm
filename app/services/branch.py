from app.database.branch import (
    get_branch_by_inn,
    get_branch_by_id,
    add_branch,
    get_all_branches,
)
from app.config.config import ApplicationException
from app.schemas.common import to_schema
from app.schemas.branch import BranchItem


async def get_branch_list(session, query):
    branches = await get_all_branches(session, query)

    if not branches:
        raise ApplicationException("Company List Not found", 404)

    return {
        "items": branches.items,
        "total": branches.total,
        "limit": query.limit,
        "offset": query.offset,
    }


async def get_branch(session, branch_id):
    branch = await get_branch_by_id(session, branch_id)
    if not branch:
        raise ApplicationException("Company Not found", 404)

    if branch.is_archived:
        raise ApplicationException(f"A company '{branch.name}' is archived", 400)

    return to_schema(BranchItem, branch)


async def change_branch(session, branch_id, item):
    branch = await get_branch_by_id(session, branch_id)
    if not branch:
        raise ApplicationException("Company Not found", 404)

    if branch.is_archived:
        raise ApplicationException(f"A company '{branch.name}' is archived", 400)

    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():
        setattr(branch, name, value)

    return to_schema(BranchItem, branch)


async def create_branch(session, inn, branch_name):
    branch = await get_branch_by_inn(session, inn)
    if branch:
        if branch.is_archived:
            raise ApplicationException("Company is archived", 400, {"inn": branch.inn})

        raise ApplicationException(f"A company with INN '{inn}' already exists", 400)

    new_branch = await add_branch(session, inn, branch_name)
    return new_branch


async def archive_branch(session, id):

    branch = await get_branch_by_id(session, id)

    if not branch:
        raise ApplicationException("Company Not found", 404)

    if branch.is_archived:
        raise ApplicationException(f"A company with INN {branch.inn} is archived", 400)

    branch.is_archived = True
    return branch


async def restore_branch(session, id):
    branch = await get_branch_by_id(session, id)

    if not branch:
        raise ApplicationException("Contractor Not found", 404)

    if not branch.is_archived:
        raise ApplicationException("Contractor is already active", 400)

    branch.is_archived = False
    return branch
