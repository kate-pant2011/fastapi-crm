from app.config.config import ApplicationException
from app.schemas.stage import StageItem
from app.database.project import get_project_by_id
from app.schemas.common import to_schema
from app.database.stage import (
    get_filtered_stages,
    add_stage,
    get_stage_by_id,
)
from .common import Access

async def get_stage_list(session, roles, requester_id, project_id, query):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(requester_id)

    project = await get_project_by_id(session, project_id, manager_id)
    if not project:
        raise ApplicationException("Project Not Found", 404)

    if project.is_archived:
        raise ApplicationException("Project is archived", 400)

    stages = await get_filtered_stages(
        session=session, 
        manager_id=manager_id, 
        project_id=project_id, 
        query=query
    )

    if not stages:
        raise ApplicationException("Stages Not Found", 404)

    return {"items": stages.items, "total": stages.total, "limit": query.limit, "offset": query.offset}


async def get_stage(session, roles, requester_id, project_id, stage_id):
    access = Access(roles)
    access.require_admin_or_manager()
    is_admin = access.is_admin()
    executor_id = access.executor_id(requester_id)
    manager_id = access.manager_id(requester_id)

    project = await get_project_by_id(session, project_id, manager_id, executor_id)
    if not project:
        raise ApplicationException("Project Not Found", 404)

    if project.is_archived:
        raise ApplicationException("Project is archived", 400)

    stage = await get_stage_by_id(session, stage_id, requester_id, is_admin)
    if not stage:
        raise ApplicationException("stage Not found", 404)

    if stage.is_archived:
        raise ApplicationException("stage is deleted", 400)

    return to_schema(StageItem, stage)


async def change_stage(session, roles, user_id, project_id, stage_id, item):
    access = Access(roles)
    access.require_admin_or_manager()
    is_admin = access.is_admin()
    executor_id = access.executor_id(user_id)
    manager_id = access.manager_id(user_id)

    project = await get_project_by_id(session, project_id, manager_id, executor_id)
    if not project:
        raise ApplicationException("Project Not Found", 404)

    if project.is_archived:
        raise ApplicationException("Project is archived", 400)
    
    stage = await get_stage_by_id(session, stage_id, user_id, is_admin)
    if not stage:
        raise ApplicationException("Stage Not found", 404)

    if stage.is_archived:
        raise ApplicationException(f"A stage '{stage.name}' is archived", 400)
    
    update_data = item.model_dump(exclude_unset=True)

    start_date = update_data.get("start_date", None) or stage.start_date
    end_date = update_data.get("end_date", None) or stage.end_date

    if start_date > end_date:
        raise ApplicationException("End-date cannot be less than start-date", 400)
    
    for name, value in update_data.items():   
        setattr(stage, name, value)

    return to_schema(StageItem, stage)


async def create_stage(session, data, manager_id):
    project = await get_project_by_id(session, data.project_id, manager_id)
    if not project:
        raise ApplicationException("project Not found", 404)

    if project.is_archived:
        raise ApplicationException("project is deleted", 400)

    if data.start_date > data.end_date:
        raise ApplicationException("End-date cannot be less than start-date", 400)
    
    new_stage = await add_stage(session, data)

    return new_stage


async def archive_stage(session, stage_id, manager_id, project_id):
    project = await get_project_by_id(session, project_id, manager_id)
    if not project:
        raise ApplicationException("Project Not Found", 404)

    if project.is_archived:
        raise ApplicationException("Project is archived", 400)
    
    stage = await get_stage_by_id(session, stage_id, manager_id, is_admin=None)

    if not stage:
        raise ApplicationException("stage Not found", 404)

    if stage.is_archived:
        raise ApplicationException("stage is already archived", 400)

    stage.is_archived = True
    return stage


async def restore_stage(session, stage_id, roles, requester_id, project_id):
    access = Access(roles)
    access.require_admin_or_manager()
    is_admin = access.is_admin()
    manager_id = access.manager_id(requester_id)
    
    project = await get_project_by_id(session, project_id, manager_id)
    if not project:
        raise ApplicationException("Project Not Found", 404)

    if project.is_archived:
        raise ApplicationException("Project is archived", 400)

    stage = await get_stage_by_id(session, stage_id, requester_id, is_admin)

    if not stage:
        raise ApplicationException("Stage Not found", 404)

    if stage.is_archived is False:
        raise ApplicationException("Stage is already active", 400)

    stage.is_archived = False
    return stage




