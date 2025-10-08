from pydantic import BaseModel


class BookmarkCategoryCreateDto(BaseModel):
    category_uuid: str
    bookmark_uuid: str
