from app.database.assignment import (
    add_assignment,
    get_assignment_by_id,
)
from app.config.config import ApplicationException
from app.schemas.common import to_schema
from app.schemas.assignment import AssignmentItem
from .common import Access
from app.database.stage import get_stage_by_id
from app.database.user import get_user_by_id
from .contractor import get_contractor


async def get_assignment(session, roles, requester_id, assignment_id):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(requester_id)

    assignment = await get_assignment_by_id(session, assignment_id, manager_id)

    if not assignment:
        raise ApplicationException("Assignment Not found", 404)

    return to_schema(AssignmentItem, assignment)


async def change_assignment(session, assignment_id, item, roles, user_id):
    manager_id = Access(roles).manager_id(user_id)

    assignment = await get_assignment_by_id(session, assignment_id, manager_id)
    if not assignment:
        raise ApplicationException("Assignment Not found", 404)

    if assignment.is_archived:
        raise ApplicationException(f"Assignment '{assignment.name}' is archived", 400)

    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():
        setattr(assignment, name, value)

    return to_schema(AssignmentItem, assignment)


async def create_assignment(session, data, manager_id):
    stage = await get_stage_by_id(session, data.stage_id, manager_id, is_admin=False)
    if not stage:
        raise ApplicationException("stage Not found", 404)

    if stage.is_archived:
        raise ApplicationException("stage is deleted", 400)

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
        if not contractor:
            raise ApplicationException("Contractor Not found", 404)

    new_assignment = await add_assignment(session, data)
    return new_assignment
