from app.database.branch import (
    get_branch_by_inn,
    get_branch_by_id,
    add_branch,
    get_all_branches,
    get_branch_by_id_with_stamp
)
from app.config.config import ApplicationException
from app.schemas.common import to_schema
from app.schemas.branch import BranchItem
from app.file_handler import FileHandler
from .common import Access
from app.audit.common import audit

sorting_rules = {
    "inn": ("inn",), 
    "name": ("name",)
}

async def get_branch_list(session, query):
    branches = await get_all_branches(session, query, sorting_rules)

    if not branches:
        raise ApplicationException("Список компаний не найден", 404)

    return {
        "items": branches.items,
        "total": branches.total,
        "limit": query.limit,
        "offset": query.offset,
    }


async def get_branch(session, branch_id):
    branch = await get_branch_by_id(session, branch_id)

    if not branch:
        raise ApplicationException("Компания не найдена", 404)

    return to_schema(BranchItem, branch)


async def change_branch(session, branch_id, item):
    branch = await get_branch_by_id(session, branch_id)
    
    if not branch:
        raise ApplicationException("Компания не найдена", 404)

    if branch.is_archived:
        raise ApplicationException(f"Компания '{branch.name}' архивирована", 400, {"id": branch.id})

    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():
        setattr(branch, name, value)

    return to_schema(BranchItem, branch)


async def create_branch(session, inn, branch_name):
    branch = await get_branch_by_inn(session, inn)
    if branch:
        if branch.is_archived:
            raise ApplicationException("Компания архивирована", 400, {"inn": branch.inn}, {"id": branch.id})

        raise ApplicationException(f"Компания с ИНН'{inn}' уже существует", 400)

    new_branch = await add_branch(session, inn, branch_name)
    return new_branch


async def archive_branch(session, id):

    branch = await get_branch_by_id(session, id)

    if not branch:
        raise ApplicationException("Компания не найдена", 404)

    if branch.is_archived:
        raise ApplicationException(f"Компания с ИНН {branch.inn} архивирована", 400)

    branch.is_archived = True
    return branch


async def restore_branch(session, id):
    branch = await get_branch_by_id(session, id)

    if not branch:
        raise ApplicationException("Компания не найдена", 404)

    if not branch.is_archived:
        raise ApplicationException("Компания уже восстановлена", 400)

    branch.is_archived = False
    return branch


async def download_stamp(session, branch_id, user_id):
    branch = await get_branch_by_id_with_stamp(session, branch_id)

    if not branch:
        raise ApplicationException("Компания не найдена", 404)

    if branch.is_archived:
        raise ApplicationException(f"Компания '{branch.name}' архивирована", 400, {"id": branch.id})

    if not branch.stamp_file_id:
        raise ApplicationException("Печать не найдена", 404)

    return branch.stamp_file


async def delete_stamp(session, branch_id, user_id, roles):
    access = Access(roles)
    is_admin = access.is_admin()
    branch = await get_branch_by_id_with_stamp(session, branch_id)
    

    if not branch:
        raise ApplicationException("Компания не найдена", 404)

    if branch.is_archived:
        raise ApplicationException(f"Компания с ИНН {branch.inn} архивирована", 400)

    if not branch.stamp_file_id:
        raise ApplicationException("Печать не найдена", 404)
    
    if not(is_admin or branch.stamp_file.creator_id == user_id
    ):
        audit.access_denied(
            user_id=user_id, 
            entity_id=branch_id,
            entity_name="branch"
        )

        raise ApplicationException("Компания не найдена", 404)
    
    handler = FileHandler()
    handler.delete_file(branch.stamp_file.path)
    branch.stamp_file_id = None

    await session.delete(branch.stamp_file)

    return branch

