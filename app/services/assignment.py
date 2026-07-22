from app.database.assignment import (
    add_assignment,
    get_assignment_by_id,
    get_filtered_assignments
)
from app.config.config import ApplicationException
from app.schemas.common import to_schema
from app.schemas.assignment import AssignmentItem
from .common import Access
from app.database.stage import get_stage_by_id
from app.database.user import get_user_by_id
from .contractor import get_contractor

sorting_rules = {"name": ("name",)}

async def form_assignment_list(session, query):
    assignments = await get_filtered_assignments(session, query, sorting_rules)

    if not assignments:
        assignments.items = []
        assignments.total = 0

    return {
        "items": assignments.items,
        "total": assignments.total,
        "limit": query.limit,
        "offset": query.offset,
    }


async def get_assignments_me(session, query, user_id):
    assignments = await get_filtered_assignments(session, query, sorting_rules, user_id)

    if not assignments:
        assignments.items = []
        assignments.total = 0

    return {
        "items": assignments.items,
        "total": assignments.total,
        "limit": query.limit,
        "offset": query.offset,
    }


async def get_assignment(session, roles, requester_id, assignment_id):
    access = Access(roles)
    executor_id = access.executor_id(requester_id)
    manager_id = access.manager_id(requester_id)

    assignment = await get_assignment_by_id(
        session, assignment_id, manager_id, executor_id
    )

    if not assignment:
        raise ApplicationException("Assignment Not found", 404)

    return to_schema(AssignmentItem, assignment)


async def change_assignment(session, assignment_id, item, roles, user_id):
    manager_id = Access(roles).manager_id(user_id)

    assignment = await get_assignment_by_id(session, assignment_id, manager_id)
    if not assignment:
        raise ApplicationException("Assignment Not found", 404)

    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():
        setattr(assignment, name, value)

    return to_schema(AssignmentItem, assignment)


async def create_assignment(session, data, manager_id):
    if data.contractor_id and data.user_id:
        raise ApplicationException("Assignment cannot have both contractor and user", 400)
    
    stage = await get_stage_by_id(session, data.stage_id, manager_id, is_admin=False)
    if not stage:
        raise ApplicationException("stage Not found", 404)

    if stage.is_archived:
        raise ApplicationException("stage is archived", 400)

    if data.user_id is not None:
        user = await get_user_by_id(session, data.user_id)
        if not user:
            raise ApplicationException("User Not found", 404)

        if not user.is_active:
            raise ApplicationException("User is archived", 400)

        target_roles = list({role.name for role in user.roles})
        if not target_roles:
            raise ApplicationException("Roles Not found", 404)

        is_executor = Access(target_roles).is_executor()
        if not is_executor:
            raise ApplicationException(
                f"Cannot assign user with {target_roles} status", 403
            )

    if data.contractor_id is not None:
        contractor = await get_contractor(session, data.contractor_id)

    new_assignment = await add_assignment(session, data)
    return new_assignment


async def delete_assignment(session, id, manager_id):
    assignment = await get_assignment_by_id(
        session=session, id=id, manager_id=manager_id
    )
            
    if not assignment:
        raise ApplicationException("Назначение не найдено, либо у вас нет прав!", 404)

    await session.delete(assignment)
    return assignment

    