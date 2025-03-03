from datetime import datetime, timedelta, timezone
from typing import Annotated
import os
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from models.user import User, UserRole

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.environ["PASSWORD_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("user_id")
        email = payload.get("email")
        roles = payload.get("roles", [UserRole.USER])

        if username is None or user_id is None:
            raise credentials_exception
        
        user = User(id=user_id, username=username, email=email, roles=roles)
        return user
    
    except InvalidTokenError:
        raise credentials_exception
    
    except ExpiredSignatureError:
        raise credentials_exception

def create_access_token(user: User, expires_delta: timedelta | None = None):
    to_encode = {
        "sub": user.username,
        "email": user.email,
        "user_id": user.id,
        "roles": user.roles
    }
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def has_role(required_role: str):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if required_role not in current_user.roles:
            logging.error(f"User {current_user.username} does not have required role {required_role}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return role_checker

admin_required = has_role(UserRole.ADMIN)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)