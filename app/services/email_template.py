from app.config.config import ApplicationException
from app.schemas.email_template import EmailTemplateItem
from app.schemas.common import to_schema
from app.database.email_template import (
    add_email_template,
    get_all_email_templates,
    get_email_template_by_id,
    get_email_template_by_name,
)
from app.services.common import Access    
from app.database.project import get_project_by_id
from app.database.user import get_user_by_id
from app.database.stage import get_stage_by_id
from app.database.client import get_client_by_id
from app.database.company import get_company_by_id
from app.database.contract import get_contract_by_id


VARIABLE_RESOLVERS = {
    "project_name": lambda ctx: ctx["project"].name if ctx.get("project") else "PROJECT NAME",
    "client_name": lambda ctx: ctx["client"].name if ctx.get("client") else "CLIENT NAME",
    "contract_name": lambda ctx: ctx["contract"].name if ctx.get("contract") else "CONTRACT NAME",
    "contract_number": lambda ctx: ctx["contract"].number if ctx.get("contract") else "CONTRACT NUMBER",
    "company_name": lambda ctx: ctx["company"].name if ctx.get("company") else "COMPANY NAME",
    "stage_name": lambda ctx: ctx["stage"].name if ctx.get("stage") else "STAGE NAME",
    "user_name": lambda ctx: ctx["user"].name if ctx.get("user") else "NAME",
    "user_surname": lambda ctx: ctx["user"].surname if ctx.get("user") else "SURNAME",
    "user_position":lambda ctx: ctx["user"].position if ctx.get("user") else "POSITION",
    "user_email": lambda ctx: ctx["user"].email if ctx.get("user") else "EMAIL",
}


def get_email_template_vars():   
    return {"variables": list(VARIABLE_RESOLVERS.keys())}


async def get_email_template_list(session, scope, limit, offset, roles, user_id):
    is_admin = Access(roles).is_admin()

    templates = await get_all_email_templates(
        session=session, scope=scope, limit=limit, offset=offset, is_admin=is_admin, user_id=user_id
    )
    if not templates.items:
        raise ApplicationException("Templates Not Found", 404)

    return {
        "items": templates.items,
        "total": templates.total,
        "limit": limit,
        "offset": offset,
    }


async def get_email_template(session, template_id, roles, user_id):
    is_admin = Access(roles).is_admin()

    template = await get_email_template_by_id(session, template_id)

    if not template:
        raise ApplicationException("Template Not found", 404)
    
    if not template.is_public:

        if not is_admin or not template.creator_id == user_id:
            raise ApplicationException("Cannot use this template", 403)

    return to_schema(EmailTemplateItem, template)


async def create_email_template(session, data, creator_id):
    template = await get_email_template_by_name(session, data.name)

    if template:
        raise ApplicationException(
            f"Template named {data.name} already exists", 400
        )

    new_template = await add_email_template(session, data, creator_id)
    return new_template


async def change_email_template(session, item, user_id, roles, template_id):
    template = await get_email_template_by_id(session, template_id)

    if not template:
        raise ApplicationException("Template Not found", 404)

    if user_id != template.creator_id:
        raise ApplicationException("Only template-creator can make changes", 403)

    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():
        setattr(template, name, value)

    return to_schema(EmailTemplateItem, template)



async def delete_email_template(session, user_id, roles, template_id):
    template = await get_email_template_by_id(session, template_id)
    if not template:
        raise ApplicationException("Template Not found", 404)

    if user_id != template.creator.id:
        raise ApplicationException("Only template-creator can delete template", 403)

    await session.delete(template)

    return {"result": "deleted"}


async def render_email_template(session, user_id, roles, template_id, query):
    is_admin = Access(roles).is_admin()

    template = await get_email_template_by_id(session, template_id)

    if not template:
        raise ApplicationException("Template Not found", 404)

    if not template.is_public:
        if not is_admin and template.creator_id != user_id:
            raise ApplicationException("Cannot use this template", 403)

    ctx_objects = await build_ctx_objects(session, query, user_id, is_admin)
    context = build_context(ctx_objects)

    subject = template.subject_content.format_map(SafeDict(context))
    body = template.body_content.format_map(SafeDict(context))

    return {"subject": subject, "body": body}


class SafeDict(dict):
    def __missing__(self, key):
        return "EMPTY"


def build_context(ctx):
    return {
        key: resolver(ctx)
        for key, resolver in VARIABLE_RESOLVERS.items()
    }


async def build_ctx_objects(session, query, user_id, is_admin):
    ctx = {}

    if query.stage_id:
        stage = await get_stage_by_id(session, query.stage_id, user_id, is_admin)
        ctx["stage"] = stage
        ctx["project"] = safe_get(stage, "project")
        ctx["client"] = safe_get(stage, "project", "client")
        ctx["contract"] = safe_get(stage, "project", "contract")
        ctx["company"] = safe_get(stage, "project", "contract", "company")

    elif query.project_id:
        project = await get_project_by_id(session, query.project_id)
        ctx["project"] = project
        ctx["client"] = safe_get(project, "client")
        ctx["contract"] = safe_get(project, "contract")
        ctx["company"] = safe_get(project, "contract", "company")

    elif query.contract_id:
        contract = await get_contract_by_id(session, query.contract_id)
        ctx["contract"] = contract
        ctx["company"] = safe_get(contract, "company")
        ctx["client"] = safe_get(contract, "company", "client")

    elif query.company_id:
        company = await get_company_by_id(session, query.company_id)
        ctx["company"] = company
        ctx["client"] = safe_get(company, "client")

    elif query.client_id:
        client = await get_client_by_id(session, query.client_id)
        ctx["client"] = client

    if query.user_id:
        user = await get_user_by_id(session, query.user_id)
        ctx["user"] = user

    return ctx

def safe_get(obj, *attrs):
    result = obj

    for attr in attrs:
        result = getattr(result, attr, None) if result else None

    return result


