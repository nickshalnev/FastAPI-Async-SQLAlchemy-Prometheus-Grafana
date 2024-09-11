import os
import time
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.auth.exceptions import credentials_exception
from src.auth.models import User
from src.auth.schemas import CreateUserReq
from src.config import logger

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: int = None):
    logger.debug("Creating access token")
    to_encode = data.copy()
    if expires_delta:
        expire = time.time() + expires_delta
    else:
        expire = time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug("Created")
    return encoded_jwt


async def create_user(user: CreateUserReq, db: AsyncSession):
    logger.debug(f"Creating user {user.email}")
    db_user = User(email=user.email,
                   name=user.name,
                   hashed_password=get_password_hash(user.password),
                   last_login=int(time.time()))
    db.add(db_user)
    await db.commit()
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
    await db.commit()
    logger.debug("User authenticated")
    return user


async def refresh_user_token(token: str, db: AsyncSession):
    logger.debug("Refreshing token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Invalid token")
            raise credentials_exception
    except JWTError:
        logger.warning("Invalid token")
        raise credentials_exception

    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if user is None:
        logger.warning(f"No user found for email: {email}")
        raise credentials_exception

    user.last_login = int(time.time())
    await db.commit()

    access_token = create_access_token(data={"sub": user.email})
    logger.debug("Token refreshed")
    return {"access_token": access_token, "token_type": "bearer"}
