from fastapi import APIRouter, Depends, HTTPException, Query
from app.config.config import ApplicationException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_roles
from app.auth.dependencies import UserDTO
from app.config.connection import get_db
from app.schemas.common import BaseShortResponse, BaseListResponse
from app.schemas.assignment import (
    AssignmentItem,
    AssignmentCreation,
    AssignmentPatchRequest,
)
from app.services.assignment import (
    form_assignment_list,
    get_assignment, 
    get_assignments_me,
    create_assignment, 
    change_assignment, 
    delete_assignment
)
from dataclasses import dataclass
from typing import Literal


assignment_router = APIRouter()


@dataclass
class AssignmentQueryDTO:
    sort: str | None
    limit: int = 20
    offset: int = 0
    is_done: bool | None = None
    scope: str | None = None

@assignment_router.get("/assignment", response_model=BaseListResponse)
async def client_list(
    is_done: bool | None = Query(default=None),
    scope: Literal["users", "contractors"] | None = Query(
        default=None, 
        description="Filter: either users or contractors list"
    ),
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin")),
):
    try:
        query = AssignmentQueryDTO( 
            sort=sort, 
            limit=limit, 
            offset=offset, 
            is_done=is_done, 
            scope=scope
        )
        return await form_assignment_list(
            session=session, query=query
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")
    

@assignment_router.get("/assignments/me", response_model=BaseListResponse)
async def get_assignment_router(
    is_done: bool | None = Query(default=None),
    sort: str | None = Query(default=None, description="- stands for desc"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("executor")),
):
    try:
        query = AssignmentQueryDTO(
            sort=sort, 
            limit=limit, 
            offset=offset, 
            is_done=is_done, 
        )
        return await get_assignments_me(
            session=session, query=query, user_id=user.id
        )

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@assignment_router.get("/assignment/{id}", response_model=AssignmentItem)
async def get_assignment_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("owner", "admin", "manager", "executor")),
):
    try:
        return await get_assignment(session, user.roles, user.id, id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@assignment_router.patch("/assignment/{id}", response_model=AssignmentItem)
async def change_assignment_router(
    id: int,
    item: AssignmentPatchRequest,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager", "executor")),
):
    try:
        return await change_assignment(session, id, item, user.roles, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f" {type(e).__name__} - {e}")


@assignment_router.post("/assignment", response_model=BaseShortResponse)
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


@assignment_router.delete("/assignment/{id}", response_model=BaseShortResponse)
async def delete_assignment_router(
    id: int,
    session: AsyncSession = Depends(get_db),
    user: UserDTO = Depends(require_roles("manager")),
):
    try:
        return await delete_assignment(session, id, user.id)

    except ApplicationException as e:
        raise HTTPException(status_code=e.code, detail=e.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__} - {e}")
    

