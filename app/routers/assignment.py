from fastapi import APIRouter, Depends, HTTPException, Query
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.common import ShortItem
from app.schemas.assignment import (
    AssignmentItem,
    AssignmentCreation,
)
from app.services.assignment import (
    get_assignment,
    create_assignment,
)

assignment_router = APIRouter()


@assignment_router.get("/assignment/{id}", response_model=AssignmentItem)
async def get_assignment_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager")),
):
    try:
        return await get_assignment(session, user.roles, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@assignment_router.post("/assignment", response_model=ShortItem)
async def create_assignment_router(
    data: AssignmentCreation,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await create_assignment(session, data, user.id)

    except ApplicationException as e:
        raise HTTPException(
            status_code=e.code, detail={"message": e.name, "payload": e.payload}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")


