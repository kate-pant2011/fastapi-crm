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
        return "____________"


