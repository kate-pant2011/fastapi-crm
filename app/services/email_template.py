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
from app.services.template_context import build_context, build_ctx_objects
from app.audit.common import audit
from app.schemas.email_template import EmailRenderDTO
from app.schemas.common import BaseShortResponse
from app.email.service import get_email_list
from jinja2 import Template

async def get_email_template_list(session, scope, limit, offset, roles, user_id):
    is_admin = Access(roles).is_admin()

    templates = await get_all_email_templates(
        session=session, scope=scope, limit=limit, offset=offset, is_admin=is_admin, user_id=user_id
    )
    if not templates.items:
        return {
            "items": [],
            "total": templates.total,
            "limit": limit,
            "offset": offset,
        }

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

        if not is_admin and not template.creator_id == user_id:
            audit.access_denied(
                user_id=user_id, 
                entity_id=template_id,
                entity_name="template"
            )
            raise ApplicationException("Template Not found", 404)

    return to_schema(EmailTemplateItem, template)


async def create_email_template(session, data, creator_id):
    template = await get_email_template_by_name(session, data.name)

    if template:
        raise ApplicationException(
            f"Template named {data.name} already exists", 400
        )

    new_template = await add_email_template(session, data, creator_id)
    return to_schema(BaseShortResponse, new_template)


async def change_email_template(session, item, user_id, template_id):
    template = await get_email_template_by_id(session, template_id)

    if not template:
        raise ApplicationException("Template Not found", 404)

    if user_id != template.creator_id:
        raise ApplicationException("Only template-creator can make changes", 403)

    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():
        setattr(template, name, value)

    return to_schema(BaseShortResponse, template)



async def delete_email_template(session, user_id, roles, template_id):
    template = await get_email_template_by_id(session, template_id)
    template_name = template.name
    if not template:
        raise ApplicationException("Template Not found", 404)

    if user_id != template.creator.id:
        raise ApplicationException("Only template-creator can delete template", 403)

    await session.delete(template)

    return {"name": template_name}


async def render_email_template(session, user_id, roles, template_id, query):
    is_admin = Access(roles).is_admin()

    template = await get_email_template_by_id(session, template_id)

    if not template:
        raise ApplicationException("Template Not found", 404)

    if not template.is_public:
        if not is_admin and template.creator_id != user_id:
            audit.access_denied(
                user_id=user_id, 
                entity_id=template_id,
                entity_name="template"
            )
            raise ApplicationException("Template Not found", 404)

    ctx_objects = await build_ctx_objects(session, query, user_id, is_admin)
    context = build_context(ctx_objects)

    subject = Template(template.subject_content or "").render(**context)
    body = Template(template.body_content or "").render(**context)

    to, cc = "", ""
    client_emails = context.get("client_emails")
    if client_emails:
        client_emails = client_emails.split(", ")
        to = client_emails[0]
        if len(client_emails) > 1:
            cc = ", ".join(client_emails[1:])

    from_emails = await get_email_list(
        session=session, 
        limit=1000, 
        offset=0, 
        user_id=user_id, 
        roles=roles, 
        scope="available"
    )

    return EmailRenderDTO(
        from_emails=from_emails.get("items"),
        to=to,
        cc=cc,
        subject=subject,
        body=body,
    )


class SafeDict(dict):
    def __missing__(self, key):
        return "____________"


