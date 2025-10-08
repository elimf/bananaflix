from uuid import UUID

from pydantic import BaseModel

class LoginRequest(BaseModel):
    pseudo: str
    password: str
class UserCreate(BaseModel):
    pseudo: str
    password: str

class UserOut(BaseModel):
    id: UUID
    pseudo: str

class Token(BaseModel):
    access_token: str
    token_type: str

class GenreCreate(BaseModel):
    name: str


class CreateBookMarkDto(BaseModel):
    user_id: str
    video_id: int


class BookmarkCategoryCreateDto(BaseModel):
    category_uuid: str
    bookmark_uuid: str
class DeleteBookmarkDto(BaseModel):
    uuid: str