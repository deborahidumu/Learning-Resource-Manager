import logging
from datetime import timedelta
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm

from models.auth import Token
from models.user import User, UserCreate
from core.security import (
    get_current_user,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from core.exceptions import UserExistsError, DatabaseError
from db.user import userdb

router = APIRouter()


@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    try:
        # Log the incoming request
        logging.info(f"Login attempt for username: {form_data.username}")
        
        # Get the user
        user = await userdb.authenticate_user(form_data.username)
        
        # Check if user exists
        if user is None:
            logging.warning(f"Login attempt with non-existent username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if password matches
        if not verify_password(form_data.password, user.hashed_password):
            logging.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Authentication successful
        logging.info(f"Successful login for user: {form_data.username}")
        
        # Generate token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            user=user, expires_delta=access_token_expires
        )
        
        # Return token response
        return Token(access_token=access_token, token_type="bearer")
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the full exception for debugging
        logging.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login",
        )


@router.post("/create-user")
async def signup(
    username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
):
    user = UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
        )
    try:
        user_id = await userdb.create_user(user)
        return {"status": "success", "data": {"user_id": user_id}}

    except UserExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except DatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            # Log the database error (e)
            detail="An error occured while trying to create the user",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            # Log the unexpected error (e)
            detail="An unexpected error occured",
        )
