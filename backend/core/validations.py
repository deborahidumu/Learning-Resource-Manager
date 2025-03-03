from fastapi import HTTPException, status
import re

from models.user import User

def validate_user_input(user: User, password: str, confirm_password: str) -> None:
     # validating that passwords match
    if password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    # validating that username, email, password and confirm_password are not empty
    if not user.username or not user.email or not password or not confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please fill in all fields",
        )

    # validating that username is alphanumeric
    if not user.username.isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is invalid",
        )

    # validating that email is valid
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be a valid email address (e.g., user@example.com)"
        )

    # validating that password is at least 5 characters long
    if len(password) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too short, it must be atleast 5 characters long",
        )