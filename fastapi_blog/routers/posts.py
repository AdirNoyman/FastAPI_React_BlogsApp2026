from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import models.models as models
import models.schemas as schemas
from sqlalchemy.orm import selectinload
from pathlib import Path

router = APIRouter()

# Get the base directory (where main.py is located)
BASE_DIR = Path(__file__).resolve().parent


# API routes - Posts ###########################################
# GET ALL POSTS
@router.get("", response_model=list[schemas.PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)))
    posts = result.scalars().all()
    return posts

# GET SINGLE POST
@router.get("/{post_id}", response_model=schemas.PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

# CREATE POST
@router.post("", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: schemas.PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])  # Refresh the new_post instance to get the auto-generated 'id' and load the 'author' relationship for the response  
    return new_post

## UPDATE POST - FULL UPDATE
@router.put("/{post_id}", response_model=schemas.PostResponse)
async def update_post_full(post_id: int, post_data: schemas.PostCreate, db: Annotated[AsyncSession, Depends(get_db)]): 
     # TODO: add authentication and check if the current user is the author of the post before allowing updates
    # Get the post to update   
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()   
    # Get the user to ensure the provided user_id is valid
    result = await db.execute(select(models.User).where(models.User.id == post_data.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )   
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if user.id != post.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts",
        )    
   
    # Update all fields of the post
    post.title = post_data.title
    post.content = post_data.content

    await db.commit()
    await db.refresh(post, attribute_names=["author"])  # Refresh the post instance to load the updated 'author' relationship for the response
    return post
    

## UPDATE POST - PARTIAL UPDATE
@router.patch("/{post_id}", response_model=schemas.PostResponse)
async def update_post_partial(post_id: int, post_data: schemas.PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    # TODO: add authentication and check if the current user is the author of the post before allowing updates
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first() 
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") 

    # Update post fields if they are provided in the update request
    update_data = post_data.model_dump(exclude_unset=True)  #Exclude unprovided fields - Get only the fields that were provided in the request
    

    for key, value in update_data.items():
        setattr(post, key, value)

    await db.commit()
    await db.refresh(post, attribute_names=["author"])  # Refresh the post instance to load the updated 'author' relationship for the response
    return post

## GET ALL POSTS BY USER
@router.get("/{user_id}/posts", response_model=list[schemas.PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts

# DELETE POST
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    # TODO: add authentication and check if the current user is the author of the post before allowing deletion
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await db.delete(post)
    await db.commit()
    return 



