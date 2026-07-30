from app.config.config import ApplicationException
from app.database.contract import get_contract_by_id
from app.database.client import get_client_by_id
from app.database.user import get_user_by_id
from app.database.project import (
    get_filtered_projects,
    add_project,
    get_project_by_name,
    get_project_by_id,
)
from app.schemas.common import to_schema, BaseShortResponse
from app.schemas.contract import ContractItem
from .common import Access

sorting_rules = {"start_date": ("start_date", "name"), "name": ("name",)}

async def get_project_list(session, roles, requester_id, query):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id_with_scope(user_id=requester_id, scope=query.scope)

    projects = await get_filtered_projects(
        session=session, manager_id=manager_id, query=query, sorting_rules=sorting_rules
    )

    if not projects:
        raise ApplicationException("projects Not Found", 404)

    return {
        "items": projects.items,
        "total": projects.total,
        "limit": query.limit,
        "offset": query.offset,
    }


async def get_project(session, roles, requester_id, project_id):
    access = Access(roles)
    manager_id = access.manager_id(requester_id)
    executor_id = access.executor_id(requester_id)

    project = await get_project_by_id(session, project_id, manager_id, executor_id)
    if not project:
        raise ApplicationException("project Not found", 404)

    manager = project.client.manager
    if not manager:
        raise ApplicationException("manager Not found", 404)

    return {
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "client_name": project.client.name,
        "client_email": project.client.email,
        "client_id": project.client_id,
        "contract": (
            to_schema(ContractItem, project.contract) if project.contract else None
        ),
        "manager": to_schema(BaseShortResponse, manager),
        "stages": [to_schema(BaseShortResponse, stage) for stage in project.stages if not stage.is_archived],
        "is_archived": project.is_archived,
        "files": len(project.files or [])
    }


async def change_project(session, roles, user_id, project_id, item):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(user_id)

    project = await get_project_by_id(session, project_id, manager_id)

    if not project:
        raise ApplicationException("Проект не найден, либо у Вас нет прав!", 404)

    if project.is_archived:
        raise ApplicationException(f"A project '{project.name}' is archived", 400, {"id": project.id})

    manager = await get_user_by_id(session, project.client.manager_id)
    if not manager:
        raise ApplicationException("manager Not found", 404)

    update_data = item.model_dump(exclude_unset=True)

    if "contract_id" in update_data:
        contract = await get_contract_by_id(session, update_data.get("contract_id"), manager_id)
        if not contract:
            raise ApplicationException("contract Not found", 404)

        if contract.is_archived:
            raise ApplicationException("contract is archived", 400, {"id": contract.id})
        
        if project.client.id != contract.company.client.id:
            raise ApplicationException(
                "Contract and project have different client-relations", 400,
                {
                    "project_client_id": project.client.id, 
                    "contract_client_id": contract.company.client.id
                }
            )

    start_date = update_data.get("start_date", None) or project.start_date
    end_date = update_data.get("end_date", None) or project.end_date

    if start_date > end_date:
        raise ApplicationException("End-date cannot be less than start-date", 400)

    for name, value in update_data.items():
        setattr(project, name, value)

    return {
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "client_name": project.client.name,
        "client_email": project.client.email,
        "contract": (
            to_schema(ContractItem, project.contract) if project.contract else None
        ),
        "manager": to_schema(BaseShortResponse, manager),
        "stages": [to_schema(BaseShortResponse, stage) for stage in project.stages],
        "is_archived": project.is_archived,
        "files": len(project.files or [])
    }


async def create_project(session, data, manager_id):
    project = await get_project_by_name(session, data.name)

    if project:
        if project.is_archived:
            raise ApplicationException(
                f"Project  named {data.name} is archived", 400, {"id": project.id}
            )

        raise ApplicationException(f"Project named {data.name} already exists", 400)

    client = await get_client_by_id(session, data.client_id, manager_id)
    if not client:
        raise ApplicationException("client Not found", 404)

    if client.is_archived:
        raise ApplicationException("project is archived", 400, {"id": client.id})

    if data.start_date > data.end_date:
        raise ApplicationException("End-date cannot be less than start-date", 400)

    new_project = await add_project(session, data)

    return new_project


async def archive_project(session, project_id, manager_id):
    project = await get_project_by_id(session, project_id, manager_id)

    if not project:
        raise ApplicationException("Проект не найден, либо у Вас нет прав!", 404)

    if project.is_archived:
        raise ApplicationException("Проект уже архивирован!", 400)

    project.is_archived = True
    return project


async def restore_project(session, project_id, roles, requester_id):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(requester_id)

    project = await get_project_by_id(session, project_id, manager_id)

    if not project:
        raise ApplicationException("Проект не найден, либо у Вас нет прав!", 404)

    if project.is_archived is False:
        raise ApplicationException("Проект уже активен!", 400)

    project.is_archived = False
    return project
