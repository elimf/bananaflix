from app.repository import BookmarkCategoryRepository
from app.core import ResponseModel, ResponseStatus
from app.dto import BookmarkCategoryCreateDto


class BookMarkCategoryService:

    def __init__(self):
        self.bookmark_category = BookmarkCategoryRepository()

    async def create(self, title: str) -> ResponseModel[str]:
        return await self.bookmark_category.create(title)

    async def delete(self, bookmark_category_id: str) -> ResponseModel[str]:
        return await self.bookmark_category.delete(bookmark_category_id)

    async def add_bookmark_to_category(self, body: BookmarkCategoryCreateDto) -> ResponseModel[str]:
        return await self.bookmark_category.add_bookmark_to_category(body)
