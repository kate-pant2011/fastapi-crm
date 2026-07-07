from app.config.config import ApplicationException
from app.schemas.doc_template import DocTemplateItem
from app.schemas.common import to_schema
from app.file_handler import FileHandler
from app.database.doc_template import (
    add_doc_template,
    get_all_doc_templates,
    get_doc_template_by_id,
    get_doc_template_by_name,
)
from app.database.branch import get_branch_by_id_with_stamp
from app.services.common import Access    
from app.services.template_context import build_context, build_ctx_objects
from app.services.file import upload_file
from app.database.generated_doc import add_generated_doc
from app.database.file import add_file
from app.file_handler import FileUploadDTO, FileNameDTO
from datetime import datetime
from docx import Document
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from app.audit.documents import docs_audit
import re
import uuid
import os
import logging

logger = logging.getLogger(__name__)


async def get_doc_template_list(session, scope, limit, offset, roles, user_id):
    is_admin = Access(roles).is_admin()

    templates = await get_all_doc_templates(
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


async def get_doc_template(session, template_id, roles, user_id):
    is_admin = Access(roles).is_admin()

    template = await get_doc_template_by_id(session, template_id)

    if not template:
        raise ApplicationException("Template Not found", 404)
    
    if not template.is_public:
            if not is_admin and not template.creator_id == user_id:
                docs_audit.template_access_denied(
                    user_id=user_id, 
                    template_id=template_id, 
                    template_name=template.name, 
                    reason="Access to template denied"
                )
            raise ApplicationException("Template id not found", 404)

    return to_schema(DocTemplateItem, template)


async def change_doc_template(session, item, user_id, template_id):
    template = await get_doc_template_by_id(session, template_id)

    if not template:
        raise ApplicationException("Template Not found", 404)

    if user_id != template.creator_id:
        docs_audit.template_access_denied(
            user_id=user_id, 
            template_id=template_id, 
            template_name=template.name, 
            reason="Only creator can edit"
        )

        raise ApplicationException("Only template-creator can make changes", 403)

    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():
        setattr(template, name, value)

    docs_audit.template_updated(
        user_id=user_id, 
        template_id=template_id, 
        template_name=template.name
    )

    return to_schema(DocTemplateItem, template)


async def delete_doc_template(session, user_id, template_id):
    template = await get_doc_template_by_id(session, template_id)
    if not template:
        raise ApplicationException("Template Not found", 404)

    if user_id != template.creator.id:
        docs_audit.template_access_denied(
            user_id=user_id, 
            template_id=template_id, 
            template_name=template.name, 
            reason="Only creator can delete"
        )

        raise ApplicationException("Only template-creator can delete template", 403)
    
    handler = FileHandler()

    try:
        deleted = handler.delete_file(template.file.path)

        if not deleted:
            raise ApplicationException("Failed to delete file", 400)

        await session.delete(template)
        
    except Exception:
        logger.exception("deleting file error")
        await session.rollback()
        raise

    return {"result": "deleted"}


async def create_doc_template(session, data, creator_id, roles, file):
    template = await get_doc_template_by_name(session, data.name)

    if template:
        raise ApplicationException(
            f"Template named {data.name} already exists", 400
        )
    
    new_template = await add_doc_template(session, data, creator_id)

    uploaded_files = await upload_file(
        session=session, 
        user_id=creator_id, 
        roles=roles,
        files=[file], 
        entity_id=new_template.id,
        entity_type="template"
    )

    uploaded_file = uploaded_files[0]

    variables = extract_variables_from_docx(uploaded_file.path)

    new_template.variables = variables

    docs_audit.template_created(
        user_id=creator_id, 
        template_id=new_template.id, 
        template_name=data.name
    )

    return new_template


def extract_variables_from_docx(file_path):
    document = Document(file_path)
    text = "\n".join(p.text for p in document.paragraphs)
    pattern = r"\{\{\s*(\w+)\s*\}\}"
    variables = re.findall(pattern, text)

    return list(set(variables))
    

async def render_doc_template(session, user_id, roles, template_id, query):
    is_admin = Access(roles).is_admin()

    template = await get_doc_template_by_id(session, template_id)
    if not template:
        raise ApplicationException("Template Not found", 404)
    
    if not template.is_public:
        if not is_admin and template.creator_id != user_id:
            docs_audit.template_access_denied(
                user_id=user_id, 
                template_id=template_id, 
                template_name=template.name, 
                reason="Access to template denied"
            )
            raise ApplicationException("Template not found", 404)
    
    if not template.file:
        raise ApplicationException("This template has no files", 400)

    doc = DocxTemplate(template.file.path)

    ctx_objects = await build_ctx_objects(session, query, user_id, is_admin)
    context = build_context(ctx_objects)

    if query.branch_id:
        branch = await get_branch_by_id_with_stamp(session, query.branch_id)

        if branch:
            context["branch_name"] = branch.name

            if branch.stamp_file:            
                if query.stamp_width_mm is not None:
                    branch.stamp_width_mm = query.stamp_width_mm

                context["stamp"] = InlineImage(
                    doc,
                    branch.stamp_file.path,
                    width=Mm(branch.stamp_width_mm)
                )

    try:
        doc.render(context)

        unique_name = f"{uuid.uuid4().hex}.docx"
        output_path = os.path.join(
            "./uploads",
            unique_name
        )

        doc.save(output_path) 

    except Exception as e:
        logger.exception("Bad file error")
        raise ApplicationException(f"Something went wrong", 400)

    size = os.path.getsize(output_path)
    now = datetime.now().strftime("%Y%m%d%H%M")
    data = FileUploadDTO(
        filenames=FileNameDTO(
            original=f"{template.name}_{now}.docx",
            unique=unique_name
        ),
        path=output_path,
        size=size,
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    file = await add_file(session, data, user_id)
    generated_doc = await add_generated_doc(session, template_id, user_id, file.id)

    docs_audit.document_generated(
        user_id=user_id, 
        file_id=file.id, 
        file_name=file.name, 
        template_id=template_id
    )
    return {
        "doc_id": generated_doc.id,
        "file_id": file.id,
        "filename": file.name,
    }
    

