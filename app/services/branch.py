from app.database.branch import get_company_by_inn, get_company_by_id, add_branch, archive_branch, activate_branch, get_all_branches
from app.config.config import ApplicationException


async def form_branch_list(session):
    branches = await get_all_branches(session)

    if not branches:
        raise ApplicationException("Company List Not found", 404)
    
    return branches

async def get_branch(session, id):
    branch = await get_company_by_id(session, id)
    if not branch:
        raise ApplicationException("Company Not found", 404)

    if branch.is_deleted:
        raise ApplicationException(f"A company '{branch.name}' is deleted", 400)
    return branch
        

async def create_branch(session,inn, branch_name):
    company = await get_company_by_inn(session, inn)
    if company:
        if company.is_deleted:
            raise ApplicationException("Company is archived", 400, {"inn": company.inn})
        
        raise ApplicationException(f"A company with INN '{inn}' already exists", 400)
    
    await add_branch(session, inn, branch_name)    
    return { "inn": inn, "branch_name": branch_name}

async def delete_existing_branch(session, inn):

    branch = await get_company_by_inn(session, inn)

    if not branch:
        raise ApplicationException("Company Not found", 404)

    if branch.is_deleted:
        raise ApplicationException(f"A company with INN {inn} is deleted", 400)
    
    await archive_branch(session, inn)
    return True

async def restore_branch(session, inn):
    branch = await get_company_by_inn(session, inn)

    if not branch:
        raise ApplicationException("Contractor Not found", 404)
    
    if not branch.is_deleted:
        raise ApplicationException("Contractor is already active", 400)    

    await activate_branch(session, branch)   
    return True