from app.database.project import get_project_by_id
from app.database.user import get_user_by_id
from app.database.stage import get_stage_by_id
from app.database.client import get_client_by_id
from app.database.company import get_company_by_id
from app.database.contract import get_contract_by_id
from app.database.branch import get_branch_by_id

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
    "branch_name":lambda ctx: "BRANCH NAME",
    "stamp": lambda ctx: "",
}


def get_template_vars():   
    return {"variables": list(VARIABLE_RESOLVERS.keys())}


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


