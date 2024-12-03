import os
import time
from typing import Dict

from jose import jwt
import hashlib

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth.exceptions import credentials_exception, user_already_exist_exception, unhandled_exception
from src.auth.models import User
from src.auth.schemas import CreateUserReq
from src.config import logger

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 30 * 60


def verify_password(plain_password, hashed_password):
    return get_password_hash(plain_password) == hashed_password


def get_password_hash(password):
    return hashlib.md5(password.encode()).hexdigest()


async def create_user(user: CreateUserReq, db: AsyncSession):
    logger.debug(f"Creating user {user.email}")
    db_user = User(email=user.email,
                   name=user.name,
                   hashed_password=get_password_hash(user.password),
                   last_login=int(time.time()))
    db.add(db_user)
    try:
        await db.commit()
    except IntegrityError as e:
        logger.error(f"User {user.email} already exist\nReturning 409")
        raise user_already_exist_exception
    except Exception as e:
        logger.error(f"Unhandled exception: {e.__class__.__name__}\nDetials: {e}\nreturning 400")
        raise unhandled_exception
    await db.refresh(db_user)
    logger.debug("User created")
    return db_user


async def authenticate_user(email: str, password: str, db: AsyncSession):
    logger.debug(f"Authenticating user {email}")
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        logger.debug("Wrong password")
        return False
    user.last_login = int(time.time())
    try:
        await db.commit()
    except Exception as e:
        logger.error(f"Unhandled exception: {e.__class__.__name__}\nDetials: {e}\nreturning 400")
        raise unhandled_exception
    logger.debug("User authenticated")
    return user


async def refresh_user_token(token: str):
    logger.debug("Refreshing token")
    payload = decode_jwt(token)
    email: str = payload.get("sub")
    if email is None:
        logger.warning("There is not sub(email) in provided token.")
        raise credentials_exception
    new_token = sign_jwt(email)
    logger.debug("Token refreshed")
    return new_token


def sign_jwt(user_id: str) -> Dict[str, str]:
    payload = {
        "sub": user_id,
        "expires": time.time() + ACCESS_TOKEN_EXPIRE_SECONDS
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else {}
    except:
        logger.warning("Invalid token")
        return {}


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid
