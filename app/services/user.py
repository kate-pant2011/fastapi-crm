import secrets
import string
from app.database.user import get_all_users, get_user_by_email, get_user_by_id, add_user, add_user_role, archive_user, activate_user
from app.database.branch import get_company_by_inn, get_company_by_id
from dataclasses import dataclass
from app.config.config import ApplicationException
from app.config.security import hash_password

@dataclass
class NewUserDTO:
    email: str
    password: str

@dataclass
class GetUserDTO:
    name: str
    surname: str
    position: str
    email: str
    branch: str
    roles: list[str]


async def form_user_list(session, user):
    users = await get_all_users(session, user)

    if not users:
        raise ApplicationException("User List Not found", 404)

    return users

async def get_user(session, user_id, requester):

    user = await get_user_by_id(session, user_id)
    if not user:
        raise ApplicationException("User Not found", 404)
        
    if not user.is_active:
        raise ApplicationException("User is deleted", 400)   
    
    requester_roles = {role.name for role in requester.roles}
    target_roles = list({role.name for role in user.roles})

    if not target_roles:
        raise ApplicationException("Roles Not found", 404)      
    
    is_admin = bool({"owner", "admin"}.intersection(requester_roles))
    is_executor = "executor" in target_roles

    if not is_admin and not is_executor:
        raise ApplicationException(f"Cannot access user with {target_roles} status", 403)

    if not user.branch_id:
        raise ApplicationException("Company Not found", 404)
    
    if user.branch.is_deleted:
        raise ApplicationException(f"A company {user.branch.name} is deleted", 400)     
 
    return GetUserDTO(
        name=user.name,
        surname=user.surname,
        position=user.position,
        email=user.email,
        branch=user.branch.name,
        roles=target_roles
    )



async def create_user(session, data):
    user = await get_user_by_email(session, data.email)
    if user:
        if not user.is_active:
            raise ApplicationException("User is archived", 400, {"id": user.id})
        
        raise ApplicationException(f"Email {data.email} is already used", 400)
    
    branch = await get_company_by_inn(session, data.branch_inn)
    if not branch:
        raise ApplicationException("Company Not found", 404)
    if branch.is_deleted:
        raise ApplicationException(f"A company with INN {branch.inn} is deleted", 400)        
    
    password = generate_password()
    hashed_password = hash_password(password)

    new_user = await add_user(
        session, 
        data.email, 
        hashed_password, 
        data.name, 
        data.surname, 
        data.position, 
        branch.id, 
        password_change=True
    )

    await add_user_role(session, new_user, data.role)

    return NewUserDTO(
        email=new_user.email,
        password=password
    )

def generate_password():
    symbols = string.ascii_letters + string.digits
    password = "".join(secrets.choice(symbols) for i in range(10))
    return password

async def delete_user(session, user_id):
    user = await get_user_by_id(session, user_id)

    if not user:
        raise ApplicationException("User Not found", 404)
    
    if not user.is_active:
        raise ApplicationException("User is already deleted", 400)    

    await archive_user(session,user)   
    return True

async def restore_user(session, user_id):
    user = await get_user_by_id(session, user_id)

    if not user:
        raise ApplicationException("User Not found", 404)
    
    if user.is_active:
        raise ApplicationException("CUser is already active", 400)    

    await activate_user(session, user)   
    return True