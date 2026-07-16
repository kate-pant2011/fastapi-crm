from starlette.middleware.base import BaseHTTPMiddleware
from app.config.config import settings
import jwt
from app.auth.service import update_tokens
from app.config.connection import SessionLocal


class RefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request,
        call_next,
    ):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if not access_token:
            return await call_next(request)

        try:
            jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

            return await call_next(request)

        except jwt.ExpiredSignatureError:
            pass

        except jwt.PyJWTError:
            return await call_next(request)

        #if not refresh_token:
            #return await call_next(request)

        try:
            async with SessionLocal() as session:
                async with session.begin():
                    device = request.headers.get("user-agent")
                    ip = request.client.host
                    token = await update_tokens(
                        session=session,
                        refresh_token=refresh_token,
                        device=device,
                        ip=ip,
                    )

            request.state.access_token = (
                token.access
            )
            response = await call_next(request)

            response.set_cookie(
                key="access_token",
                value=token.access,
                httponly=True,
                samesite="lax",
                secure=False,
            )
            response.set_cookie(
                key="refresh_token",
                value=token.refresh,
                httponly=True,
                samesite="lax",
                secure=False,
            )
            return response

        except Exception:
            return await call_next(request)