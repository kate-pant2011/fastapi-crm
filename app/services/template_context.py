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
    "client_emails": lambda ctx: ctx["client"].email if ctx.get("client") else "CLIENT EMAIL",
    "client_telephones": lambda ctx: ctx["client"].telephone if ctx.get("client") else "CLIENT TELEPHONE",
    "contract_name": lambda ctx: ctx["contract"].name if ctx.get("contract") else "CONTRACT NAME",
    "contract_number": lambda ctx: ctx["contract"].number if ctx.get("contract") else "CONTRACT NUMBER",
    "contract_valid_from": lambda ctx: ctx["contract"].valid_from if ctx.get("contract") else "CONTRACT VALID FROM",
    "contract_valid_to": lambda ctx: ctx["contract"].valid_to if ctx.get("contract") else "CONTRACT VALID TO",
    "company_name": lambda ctx: ctx["company"].name if ctx.get("company") else "COMPANY NAME",
    "stage_name": lambda ctx: ctx["stage"].name if ctx.get("stage") else "STAGE NAME",
    "user_name": lambda ctx: ctx["user"].name if ctx.get("user") else "NAME",
    "user_surname": lambda ctx: ctx["user"].surname if ctx.get("user") else "SURNAME",
    "user_position": lambda ctx: ctx["user"].position if ctx.get("user") else "POSITION",
    "user_email": lambda ctx: ctx["user"].email if ctx.get("user") else "EMAIL",
    "branch_name": lambda ctx: "BRANCH NAME",
    "stamp": lambda ctx: "",
    "kpp": lambda ctx: ctx["company"].kpp if ctx.get("company") else "КПП",
    "ogrn":lambda ctx: ctx["company"].ogrn if ctx.get("company") else "ОГРН",
    "okpo": lambda ctx: ctx["company"].okpo if ctx.get("company") else "ОКПО",
    "okved": lambda ctx: ctx["company"].okved if ctx.get("company") else "ОКВЭД",
    "okfs": lambda ctx: ctx["company"].okfs if ctx.get("company") else "ОКФС",
    "okopf": lambda ctx: ctx["company"].okopf if ctx.get("company") else "ОКОПФ",
    "okato": lambda ctx: ctx["company"].okato if ctx.get("company") else "ОКАТО",
    "legal_address": lambda ctx: ctx["company"].legal_address if ctx.get("company") else "ЮР.АДРЕС",
    "address": lambda ctx: ctx["company"].address if ctx.get("company") else "ФАКТ.АДРЕС",
    "email": lambda ctx: ctx["company"].email if ctx.get("company") else "ПОЧТА",
    "telephone": lambda ctx: ctx["company"].telephone if ctx.get("company") else "ТЕЛЕФОН",
    "website": lambda ctx: ctx["company"].website if ctx.get("company") else "САЙТ",
    "director_full_name": lambda ctx: ctx["company"].director_full_name if ctx.get("company") else "ПОЛНОЕ ФИО",
    "director_short_name": lambda ctx: ctx["company"].director_short_name if ctx.get("company") else "ФАМИЛИЯ+ИНИЦИАЛЫ",
    "director_position": lambda ctx: ctx["company"].director_position if ctx.get("company") else "ДОЛЖНОСТЬ РУКОВОДИТЕЛЯ",
    "authority_document": lambda ctx: ctx["company"].authority_document if ctx.get("company") else "ОСНОВАНИЕ ПОЛНОМОЧИЙ",
    "bank_name": lambda ctx: ctx["company"].bank_name if ctx.get("company") else "БАНК",
    "bik": lambda ctx: ctx["company"].bik if ctx.get("company") else "БИК",
    "checking_account": lambda ctx: ctx["company"].checking_account if ctx.get("company") else "Р/С",
    "correspondent_account": lambda ctx: ctx["company"].correspondent_account if ctx.get("company") else "К/C",
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


def add_context_for_branch(context, model):
    context["branch_name"] = model.name or "BRANCH NAME"
    context["kpp"] = model.kpp or "КПП"
    context["ogrn"] = model.ogrn or "ОГРН"
    context["okpo"] = model.okpo or "ОКПО"
    context["okved"] = model.okved or "ОКВЭД"
    context["okfs"] = model.okfs or "ОКФС"
    context["okopf"] = model.okopf or "ОКОПФ"
    context["okato"] = model.okato or "ОКАТО"
    context["legal_address"] = model.legal_address or "ЮР.АДРЕС"
    context["address"] = model.address or "ФАКТ.АДРЕС"
    context["email"] = model.email or "ПОЧТА"
    context["telephone"] = model.telephone or "ТЕЛЕФОН"
    context["website"] = model.website or "САЙТ"
    context["director_full_name"] = model.director_full_name or "ФИО"
    context["director_short_name"] = model.director_short_name or "ФАМИЛИЯ+ИНИЦИАЛЫ"
    context["director_position"] = model.director_position or "ДОЛЖНОСТЬ РУКОВОДИТЕЛЯ"
    context["authority_document"] = model.authority_document or "ОСНОВАНИЕ ПОЛНОМОЧИЙ"
    context["bank_name"] = model.bank_name or "БАНК"
    context["bik"] = model.bik or "БИК"
    context["checking_account"] = model.checking_account or "Р/С"
    context["correspondent_account"] = model.correspondent_account or "К/C"
