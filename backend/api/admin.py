from typing import Annotated
import logging

from fastapi import Depends, APIRouter, HTTPException, status

from models.user import User
from core.security import admin_required
from db.user import userdb


router = APIRouter(prefix="/admin")

@router.post("/users/{user_id}/roles/{role}")
async def add_role_to_user(
    user_id: int,
    role: str,
    current_user: Annotated[User, Depends(admin_required)]
):
    try: 
        await userdb.add_role_to_user(user_id, role)
        return {"status": "success", "message": f"Role {role} added to user {user_id} successfully"}
    except Exception as e:
        logging.error(f"Unexpected error during role addition: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login",
        )
    
@router.delete("/users/{user_id}/roles/{role}")
async def remove_role_from_user(
    user_id: int,
    role: str,
    current_user: Annotated[User, Depends(admin_required)]
):
    try: 
        await userdb.remove_role_from_user(user_id, role)
        return {"status": "success", "message": f"Role {role} removed from user {user_id} successfully"}
    except Exception as e:
        logging.error(f"Unexpected error during role removal: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during role removal",
        )