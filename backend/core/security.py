from datetime import datetime, timedelta, timezone
from typing import Annotated
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from models.user import User

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
        # role = payload.get("role")

        if username is None or user_id is None:
            raise credentials_exception
        
        user = User(id=user_id, username=username, email=email)
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
        # "role": user.role, when you implement roles which you should before the UI part is started,
        # just make sure to add the role to the User model and then you can add it here
    }
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)