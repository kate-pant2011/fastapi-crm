from app.database.project import get_project_by_for_ctx
from app.database.user import get_user_by_id
from app.database.stage import get_stage_by_id
from app.database.client import get_client_by_id
from app.database.company import get_company_by_id
from app.database.contract import get_contract_by_id
from app.database.branch import get_branch_by_id

VARIABLE_RESOLVERS = {
    "название_проекта": lambda ctx: ctx["project"].name if ctx.get("project") else "PROJECT NAME",
    "имя_клиента": lambda ctx: ctx["client"].name if ctx.get("client") else "CLIENT NAME",
    "client_emails": lambda ctx: ", ".join(ctx["client"].email or []) if ctx.get("client") else "CLIENT EMAILS",
    "телефоны_клиента": lambda ctx: ", ".join(ctx["client"].telephone or []) if ctx.get("client") else "CLIENT TELEPHONES",
    "наименование_контракта": lambda ctx: ctx["contract"].name if ctx.get("contract") else "CONTRACT NAME",
    "номер_контракта": lambda ctx: ctx["contract"].number if ctx.get("contract") else "CONTRACT NUMBER",
    "дата_заключения_контракта": lambda ctx: ctx["contract"].valid_from if ctx.get("contract") else "CONTRACT VALID FROM",
    "дата_завершения_контракта": lambda ctx: ctx["contract"].valid_to if ctx.get("contract") else "CONTRACT VALID TO",
    "наименование_компании_клиента": lambda ctx: ctx["company"].name if ctx.get("company") else "COMPANY NAME",
    "название_этапа": lambda ctx: ctx["stage"].name if ctx.get("stage") else "STAGE NAME",
    "имя": lambda ctx: ctx["user"].name if ctx.get("user") else "NAME",
    "фамилия": lambda ctx: ctx["user"].surname if ctx.get("user") else "SURNAME",
    "должность": lambda ctx: ctx["user"].position if ctx.get("user") else "POSITION",
    "личный_email": lambda ctx: ctx["user"].email if ctx.get("user") else "EMAIL",
    "название_подразделения": lambda ctx: ctx["branch"].name if ctx.get("branch") else "НАИМЕНОВАНИЕ ПОДРАЗДЕЛЕНИЯ",
    "branch_id": lambda ctx: ctx["branch"].id if ctx.get("branch") else "НАИМЕНОВАНИЕ ПОДРАЗДЕЛЕНИЯ",
    "stamp": lambda ctx: "",
    "кпп": lambda ctx: ctx["company"].kpp if ctx.get("company") else "КПП",
    "огрн":lambda ctx: ctx["company"].ogrn if ctx.get("company") else "ОГРН",
    "окпо": lambda ctx: ctx["company"].okpo if ctx.get("company") else "ОКПО",
    "оквед": lambda ctx: ctx["company"].okved if ctx.get("company") else "ОКВЭД",
    "окфс": lambda ctx: ctx["company"].okfs if ctx.get("company") else "ОКФС",
    "окопф": lambda ctx: ctx["company"].okopf if ctx.get("company") else "ОКОПФ",
    "окато": lambda ctx: ctx["company"].okato if ctx.get("company") else "ОКАТО",
    "юридический_адрес": lambda ctx: ctx["company"].legal_address if ctx.get("company") else "ЮР.АДРЕС",
    "фактический_адрес": lambda ctx: ctx["company"].address if ctx.get("company") else "ФАКТ.АДРЕС",
    "email_контракт": lambda ctx: ctx["company"].email if ctx.get("company") else "ПОЧТА",
    "телефон_контракт": lambda ctx: ctx["company"].telephone if ctx.get("company") else "ТЕЛЕФОН",
    "website_контракт": lambda ctx: ctx["company"].website if ctx.get("company") else "САЙТ",
    "фио_руководителя": lambda ctx: ctx["company"].director_full_name if ctx.get("company") else "ПОЛНОЕ ФИО",
    "фамилия_инициалы_руководителя": lambda ctx: ctx["company"].director_short_name if ctx.get("company") else "ФАМИЛИЯ+ИНИЦИАЛЫ",
    "должность_руководителя": lambda ctx: ctx["company"].director_position if ctx.get("company") else "ДОЛЖНОСТЬ РУКОВОДИТЕЛЯ",
    "основание_полномочий_руководителя": lambda ctx: ctx["company"].authority_document if ctx.get("company") else "ОСНОВАНИЕ ПОЛНОМОЧИЙ",
    "наименование_банка": lambda ctx: ctx["company"].bank_name if ctx.get("company") else "БАНК",
    "бик": lambda ctx: ctx["company"].bik if ctx.get("company") else "БИК",
    "расч_счет": lambda ctx: ctx["company"].checking_account if ctx.get("company") else "Р/С",
    "корр_счет": lambda ctx: ctx["company"].correspondent_account if ctx.get("company") else "К/C",
    "my_kpp": lambda ctx: ctx["branch"].kpp if ctx.get("branch") else "МОЙ КПП",
    "my_ogrn": lambda ctx: ctx["branch"].ogrn if ctx.get("branch") else "МОЙ ОГРН",
    "my_okpo": lambda ctx: ctx["branch"].okpo if ctx.get("branch") else "МОЙ ОКПО",
    "my_okved": lambda ctx: ctx["branch"].okved if ctx.get("branch") else "МОЙ ОКВЭД",
    "my_okfs": lambda ctx: ctx["branch"].okfs if ctx.get("branch") else "МОЙ ОКФС",
    "my_okopf": lambda ctx: ctx["branch"].okopf if ctx.get("branch") else "МОЙ ОКОПФ",
    "my_okato": lambda ctx: ctx["branch"].okato if ctx.get("branch") else "МОЙ ОКАТО",
    "my_legal_address": lambda ctx: ctx["branch"].legal_address if ctx.get("branch") else "МОЙ ЮР.АДРЕС",
    "my_address": lambda ctx: ctx["branch"].address if ctx.get("branch") else "МОЙ ФАКТ.АДРЕС",
    "my_email": lambda ctx: ctx["branch"].email if ctx.get("branch") else "МОЙ ПОЧТА",
    "my_telephone": lambda ctx: ctx["branch"].telephone if ctx.get("branch") else "МОЙ ТЕЛЕФОН",
    "my_website": lambda ctx: ctx["branch"].website if ctx.get("branch") else "МОЙ САЙТ",
    "my_director_full_name": lambda ctx: ctx["branch"].director_full_name if ctx.get("branch") else "МОЕ ФИО",
    "my_director_short_name": lambda ctx: ctx["branch"].director_short_name if ctx.get("branch") else "МОЯ ФАМИЛИЯ+ИНИЦИАЛЫ",
    "my_director_position": lambda ctx: ctx["branch"].director_position if ctx.get("branch") else "МОЯ ДОЛЖНОСТЬ РУКОВОДИТЕЛЯ",
    "my_authority_document": lambda ctx: ctx["branch"].authority_document if ctx.get("branch") else "МОЕ ОСНОВАНИЕ ПОЛНОМОЧИЙ",
    "my_bank_name": lambda ctx: ctx["branch"].bank_name if ctx.get("branch") else "МОЙ БАНК",
    "my_bik": lambda ctx: ctx["branch"].bik if ctx.get("branch") else "МОЙ БИК",
    "my_checking_account": lambda ctx: ctx["branch"].checking_account if ctx.get("branch") else "МОЙ Р/С",
    "my_correspondent_account": lambda ctx: ctx["branch"].correspondent_account if ctx.get("branch") else "МОЙ К/C",
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
        project = await get_project_by_for_ctx(session, query.project_id)
        ctx["project"] = project
        ctx["client"] = safe_get(project, "client")
        ctx["contract"] = safe_get(project, "contract")
        ctx["company"] = safe_get(project, "contract", "company")
        ctx["branch"] = safe_get(project, "contract", "branch")

    elif query.contract_id:
        contract = await get_contract_by_id(session, query.contract_id)
        ctx["contract"] = contract
        ctx["company"] = safe_get(contract, "company")
        ctx["branch"] = safe_get(contract, "branch")
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
        ctx["branch"] = safe_get(user, "branch")

    if query.branch_id:
        branch = await get_branch_by_id(session, query.branch_id)
        ctx["branch"] = branch

    return ctx


def safe_get(obj, *attrs):
    result = obj

    for attr in attrs:
        result = getattr(result, attr, None) if result else None

    return result

