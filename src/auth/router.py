from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.auth.schemas import CreateUserReq, Token, LoginUserReq
from src.auth.service import create_user, authenticate_user, refresh_user_token, sign_jwt, JWTBearer
from src.database import get_db

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

prefix = "auth"


@router.post(f"/{prefix}/create-user",
             response_model=Token,
             summary="Create a new user",
             tags=["Auth"])
@limiter.limit("3/minute")
async def create_user_route(request: Request, user: CreateUserReq, db: AsyncSession = Depends(get_db)):
    """
    Register a new user with an email, name, and password.

    - **email**: User's email address.
    - **name**: User's full name.
    - **password**: User's password.

    Example request:
    ```
    {
        "email": "user@example.com",
        "name": "John Doe",
        "password": "password123"
    }
    ```

    Example response:
    ```
    {
        "access_token": "string",
        "token_type": "bearer"
    }
    ```

    Returns a bearer token upon successful user creation.
    """
    user = await create_user(user, db)
    return sign_jwt(user.email)


@router.post(f"/{prefix}/login",
             response_model=Token,
             summary="User login",
             tags=["Auth"])
@limiter.limit("5/minute")
async def login_user(request: Request, login_user: LoginUserReq, db: AsyncSession = Depends(get_db)):
    """
    Authenticate the user with an email and password.

    - **email**: User's email address.
    - **password**: User's password.

    Example request:
    ```
    {
        "email": "user@example.com",
        "password": "password123"
    }
    ```

    Example response:
    ```
    {
        "access_token": "string",
        "token_type": "bearer"
    }
    ```

    Returns a bearer token upon successful authentication. If the credentials are invalid, a `400 Bad Request` error is returned.
    """
    user = await authenticate_user(login_user.email, login_user.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = sign_jwt(user.email)
    return access_token


@router.get(f"/{prefix}/refresh",
            response_model=Token,
            dependencies=[Depends(JWTBearer())],
            summary="Refresh user token",
            tags=["Auth"])
@limiter.limit("10/minute")
async def refresh_token(request: Request, token: str = Depends(JWTBearer())):
    """
    Refresh the user's authentication token using the existing one.

    - **token**: The existing JWT token.

    Example request:
    ```
    GET /auth/refresh
    Authorization: Bearer <token>
    ```

    Example response:
    ```
    {
        "access_token": "string",
        "token_type": "bearer"
    }
    ```

    Returns a new token if the existing token is valid. If the token is invalid or expired, a `401 Unauthorized` error is returned.
    """
    return await refresh_user_token(token)
