from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import models.models as models
import models.schemas as schemas
import shutil
from utils import generate_unique_filename
from pathlib import Path

router = APIRouter()

# Get the base directory (where main.py is located)
BASE_DIR = Path(__file__).resolve().parent

# API routes - Users ###########################################
# CREATE USER
@router.post("", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    username_exists = await db.execute(
        select(models.User).where(models.User.username == user.username)
    )
    username_exists = username_exists.scalar_one_or_none()
    if username_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already exists")
    email_result = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    email_exists = email_result.scalar_one_or_none()
    if email_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already exists")

    new_user = models.User(username=user.username,email=user.email)
    # Stage the new user data for insert
    db.add(new_user)
    # Execute and save the new user to the DB
    await db.commit()
    # Reloads the new_user instance with the data from the DB, including the auto-generated 'id' field, so we can return it in the response
    await db.refresh(new_user)
    return new_user

# GET USER BY ID
@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await db.execute(select(models.User).where(models.User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# UPDATE USER
@router.patch("/{user_id}", response_model=schemas.UserResponse)
async def update_user(user_id: int, user_data: schemas.UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await db.execute(select(models.User).where(models.User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)

    # Check if email is being updated and if it already exists for another user
    if "email" in update_data:
        email_result = await db.execute(
            select(models.User).where(
                models.User.email == update_data["email"],
                models.User.id != user_id
            )
        )
        email_exists = email_result.scalar_one_or_none()
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user

# UPLOAD PROFILE PICTURE
@router.post("/{user_id}/profile-picture", response_model=schemas.UserResponse)
async def upload_profile_picture(
    user_id: int,
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Upload a profile picture for a user.

    This endpoint demonstrates proper file handling with:
    - Filename sanitization (removes spaces, special characters)
    - File type validation (only images allowed)
    - Unique filename generation (prevents collisions)
    """
    # Get the user
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )

    # Generate a unique, sanitized filename
    # This prevents: spaces, special chars, path traversal, and filename collisions
    unique_filename = generate_unique_filename(file.filename or "profile.png")

    # Save the file to the media/profile_pics directory
    file_path = BASE_DIR / "media" / "profile_pics" / unique_filename
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update the user's image_file field
    user.image_file = unique_filename
    await db.commit()
    await db.refresh(user)

    return user