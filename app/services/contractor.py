from app.database.contractor import get_all_contractors, add_contractor, archive_contractor, get_contractor_by_name, get_contractor_by_id, activate_contractor
from app.database.branch import get_company_by_inn
from app.config.config import ApplicationException
from dataclasses import dataclass

@dataclass
class ContractorDTO:
    id: int
    name: str

@dataclass
class GETContractorDTO:
    name: str
    email: list[str] | None 
    description: str
    companies: list[str] | None 

async def form_contractor_list(session):
    contractors = await get_all_contractors(session)
    if not contractors:
        raise ApplicationException("Contractor List Not found", 404)

    return contractors

async def get_contractor(session, contractor_id):
    contractor = await get_contractor_by_id(session, contractor_id)
    if not contractor:
        raise ApplicationException("Contractor Not found", 404)
    
    if contractor.is_deleted:
        raise ApplicationException("Contractor is already deleted", 400)  
    
    contractor_companies = list({company.contractor_company for company in contractor.contract})

    return GETContractorDTO(
        name=contractor.name,
        email=contractor.email,
        description=contractor.description,
        companies=contractor_companies
    )

async def create_contractor(session, data):  
    contractor = await get_contractor_by_name(session, data.name)

    if contractor:
        if contractor.is_deleted:
            raise ApplicationException("Contractor is archived", 400, {"id": contractor.id})
        
        raise ApplicationException(f"Contractor named {data.name} already exists", 400)
    
    new_contractor = await add_contractor(session, data)
    return ContractorDTO(
        id=new_contractor.id,
        name=new_contractor.name
    )  

async def delete_contractor(session, contractor_id):
    contractor = await get_contractor_by_id(session, contractor_id)

    if not contractor:
        raise ApplicationException("Contractor Not found", 404)
    
    if contractor.is_deleted:
        raise ApplicationException("Contractor is already deleted", 400)    

    await archive_contractor(session, contractor)   
    return True

async def restore_contractor(session, contractor_id):
    contractor = await get_contractor_by_id(session, contractor_id)

    if not contractor:
        raise ApplicationException("Contractor Not found", 404)
    
    if contractor.is_deleted is False:
        raise ApplicationException("Contractor is already active", 400)    

    await activate_contractor(session, contractor)   
    return True