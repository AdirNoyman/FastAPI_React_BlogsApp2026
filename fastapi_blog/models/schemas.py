from datetime import datetime
from pydantic import BaseModel,EmailStr, ConfigDict,Field

# USERS ###################################################
class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=120)  

class UserCreate(User):
    pass
# TODO: add password field to UserCreate and handle hashing in the endpoint logic

class UserResponse(User):
    # TODO: exclude email from UserResponse if we don't want to expose it in API responses
    # 'model_config' -> Enables Pydantic to read data from SQLAlchemy models directly, allowing us to return SQLAlchemy model instances in our API responses without needing to convert them to Python dictionaries first.
    model_config = ConfigDict(from_attributes=True)
    id: int
    image_file: str | None
    image_path: str


# POSTS ###################################################
class Post(BaseModel):    
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=10)  

class PostCreate(Post):
     user_id: int  # TEMPORARY until we implement authentication and can get the user_id from the token

class PostResponse(Post):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse