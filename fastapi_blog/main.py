from fastapi import FastAPI, HTTPException, Request, status, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
import models.models as models
from database import Base, engine, get_db
import models.schemas as schemas
from pathlib import Path
from utils import generate_unique_filename
import shutil

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Get the base directory (where main.py is located)
BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.mount("/media", StaticFiles(directory=str(BASE_DIR / "media")), name="media")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# In-memory data store
# posts: list[dict] = [
#     {
#         "id": 1,
#         "author": "CoreyMSchafer",
#         "title": "Why I Love FastAPI",
#         "content": "FastAPI has quickly become my favorite Python web framework. The automatic docs, type hints, and async support make it a joy to work with. If you haven't tried it yet, I highly recommend giving it a shot!",
#         "date_posted": "December 31, 2025",
#     },
#     {
#         "id": 2,
#         "author": "GoodBoyBronx",
#         "title": "Corey Schafer Has the Best YouTube Tutorials!",
#         "content": "I just finished watching Corey's FastAPI series and I learned so much. His teaching style is clear, concise, and easy to follow. Highly recommend his channel to anyone looking to learn Python!",
#         "date_posted": "December 30, 2025",
#     },
#     {
#         "id": 3,
#         "author": "PoppyTheCoder",
#         "title": "Async/Await Finally Clicked",
#         "content": "After struggling with async programming for months, it finally clicked for me. The key insight was understanding the event loop and how coroutines yield control. Now my APIs are lightning fast!",
#         "date_posted": "December 27, 2025",
#     },
# ]

# Templates routes ###########################################
# Home and Posts List


## home
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )


## post_page
@app.get("/posts/{post_id}", include_in_schema=False, name="post")
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


## user_posts_page
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )



# API routes - Posts ###########################################
# GET ALL POSTS
@app.get("/api/posts", response_model=list[schemas.PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts

# GET SINGLE POST
@app.get("/api/posts/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

# CREATE POST
@app.post("/api/posts", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
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
    db.commit()
    db.refresh(new_post)
    return new_post

## GET ALL POSTS BY USER
@app.get("/api/users/{user_id}/posts", response_model=list[schemas.PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts

# DELETE POST
@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    # TODO: add authentication and check if the current user is the author of the post before allowing deletion
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(post)
    db.commit()
    return 

# API routes - Users ###########################################
# CREATE USER
@app.post("/api/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Annotated[Session, Depends(get_db)]):
    username_exists = db.execute(
        select(models.User).where(models.User.username == user.username)
    ).scalar_one_or_none()
    if username_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already exists")
    email_exists = db.execute(
        select(models.User).where(models.User.email == user.email)
    ).scalar_one_or_none()
    if email_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already exists")

    new_user = models.User(username=user.username,email=user.email)
    # Stage the new user data for insert
    db.add(new_user)
    # Execute and save the new user to the DB
    db.commit()
    # Reloads the new_user instance with the data from the DB, including the auto-generated 'id' field, so we can return it in the response
    db.refresh(new_user)
    return new_user

# GET USER BY ID
@app.get("/api/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(models.User).where(models.User.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# UPLOAD PROFILE PICTURE
@app.post("/api/users/{user_id}/profile-picture", response_model=schemas.UserResponse)
async def upload_profile_picture(
    user_id: int,
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Upload a profile picture for a user.

    This endpoint demonstrates proper file handling with:
    - Filename sanitization (removes spaces, special characters)
    - File type validation (only images allowed)
    - Unique filename generation (prevents collisions)
    """
    # Get the user
    user = db.execute(select(models.User).where(models.User.id == user_id)).scalar_one_or_none()
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
    db.commit()
    db.refresh(user)

    return user

# StarletteHTTPException Handler
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )
    if exception.status_code == 404:
        return templates.TemplateResponse(
            request,
            "404.html",
            {"request": request},
            status_code=404
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


# RequestValidationError Handler
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
