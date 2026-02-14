import jwt
from app.config.config import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.database.repositories.user import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 

async def get_current_user(session, token: str = Depends(oauth2_scheme)): 
    try:
        decoded = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=settings.ALGORITHM
        )
           
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await get_user_by_id(session, decoded.get("sub"))

    if not user:
        raise HTTPException(status_code=401,detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403,detail="Inactive user status")       
    
    return user

def require_roles(*allowed_roles):
    def checker(user = Depends(get_current_user)):
        user_roles = {role.name for role in user.roles}

        if not user_roles.intersection(allowed_roles):
            raise HTTPException(
                status_code=403,
                detail="Forbidden"
            )
        return user

    return checker
