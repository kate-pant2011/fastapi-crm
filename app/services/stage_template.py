from app.config.config import ApplicationException
from app.schemas.stage_template import StageTemplateItem
from app.database.project import get_project_by_id
from app.models.stage import Stage
from app.schemas.common import to_schema, BaseShortResponse
from app.schemas.contract import ContractItem
from app.database.stage_template import (
    add_stage_template,
    get_all_stage_templates,
    get_stage_template_by_id,
    get_stage_template_by_name,
)
from app.config.config import now


async def get_stage_template_list(session, creator_id, limit, offset):
    templates = await get_all_stage_templates(
        session=session, creator_id=creator_id, limit=limit, offset=offset
    )
    if not templates:
        raise ApplicationException("Templates Not Found", 404)

    return {
        "items": templates.items,
        "total": templates.total,
        "limit": limit,
        "offset": offset,
    }


async def get_stage_template(session, id):
    template = await get_stage_template_by_id(session, id)
    if not template:
        raise ApplicationException("Template Not found", 404)

    return to_schema(StageTemplateItem, template)


async def change_stage_template(session, data, user_id, id):
    template = await get_stage_template_by_id(session, id)
    if not template:
        raise ApplicationException("Template Not found", 404)

    if user_id != template.creator.id:
        raise ApplicationException("Only template-creator can make changes", 403)

    template.stage_list = data.stage_list

    return to_schema(StageTemplateItem, template)


async def create_stage_template(session, data, creator_id):
    template = await get_stage_template_by_name(session, data.name)
    if template:
        raise ApplicationException(
            f"Stage-template named {data.name} already exists", 400
        )

    new_template = await add_stage_template(session, data, creator_id)
    return new_template


async def create_stages_with_template(
    session, manager_id, project_id, stage_template_id
):
    project = await get_project_by_id(session, project_id, manager_id)
    if not project:
        raise ApplicationException("project Not found", 404)

    if project.is_archived:
        raise ApplicationException("project is archived", 400)

    template = await get_stage_template_by_id(session, stage_template_id)
    if not template:
        raise ApplicationException("Template Not found", 404)

    for position, name in enumerate(template.stage_list, start=1):
        stage = Stage(
            name=name,
            position=position,
            description=name,
            start_date=now,
            end_date=now,
            project_id=project_id,
        )

        session.add(stage)

    await session.flush()

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
        "manager": to_schema(BaseShortResponse, project.client.manager),
        "stages": [to_schema(BaseShortResponse, stage) for stage in project.stages],
    }
