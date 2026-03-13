from app.database.contractor import (
    get_all_contractors,
    add_contractor,
    get_contractor_by_name,
    get_contractor_by_id,
)
from app.config.config import ApplicationException
from app.schemas.contractor import ContractorItem
from app.schemas.common import to_schema


async def get_contractor_list(session, limit, offset):
    contractors = await get_all_contractors(session, limit, offset)
    if not contractors:
        raise ApplicationException("Contractor List Not found", 404)

    return {
        "items": contractors.items,
        "total": contractors.total,
        "limit": limit,
        "offset": offset,
    }


async def get_contractor(session, contractor_id):
    contractor = await get_contractor_by_id(session, contractor_id)
    if not contractor:
        raise ApplicationException("Contractor Not found", 404)

    if contractor.is_archived:
        raise ApplicationException("Contractor is already archived", 400)

    return to_schema(ContractorItem, contractor)


async def change_contractor(session, contractor_id, item):
    contractor = await get_contractor_by_id(session, contractor_id)
    if not contractor:
        raise ApplicationException("Contractor Not found", 404)

    if contractor.is_archived:
        raise ApplicationException(f"A contractor '{contractor.name}' is archived", 400)

    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():
        setattr(contractor, name, value)

    return to_schema(ContractorItem, contractor)


async def create_contractor(session, data):
    contractor = await get_contractor_by_name(session, data.name)

    if contractor:
        if contractor.is_archived:
            raise ApplicationException(
                f"Contractor named {data.name} is archived", 400, {"id": contractor.id}
            )

        raise ApplicationException(f"Contractor named {data.name} already exists", 400)

    new_contractor = await add_contractor(session, data)
    return new_contractor


async def archive_contractor(session, contractor_id):
    contractor = await get_contractor_by_id(session, contractor_id)

    if not contractor:
        raise ApplicationException("Contractor Not found", 404)

    if contractor.is_archived:
        raise ApplicationException("Contractor is already archived", 400)

    contractor.is_archived = True
    return contractor


async def restore_contractor(session, contractor_id):
    contractor = await get_contractor_by_id(session, contractor_id)

    if not contractor:
        raise ApplicationException("Contractor Not found", 404)

    if contractor.is_archived is False:
        raise ApplicationException("Contractor is already active", 400)

    contractor.is_archived = False
    return contractor
