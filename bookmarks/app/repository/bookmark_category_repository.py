from __future__ import annotations

from app.core import ResponseModel, ResponseStatus
from app.repository import BookMarkRepository
from app.dto.bookmark_category.bookmark_category_create_dto import BookmarkCategoryCreateDto

from common.models import BookMarkCategory, BookMarkModelCategory


class BookmarkCategoryRepository:

    def __init__(self):
        self.bookmark_repository = BookMarkRepository()

    async def create(self, title: str) -> ResponseModel[str]:
        try:
            category_exist: bool = await self.exist_by_title(title)

            if category_exist:
                return ResponseModel(
                    statusCode=409,
                    status=ResponseStatus.failed,
                    message=f"Bookmark category {title} already exist"
                )
            data: BookMarkCategory = BookMarkCategory(
                title=title
            )

            await BookMarkCategory.save(data)
            return ResponseModel(
                message=f"Bookmark category {title} added successfully",
                statusCode=200,
                status=ResponseStatus.success
            )
        except Exception as e:
            return ResponseModel(
                statusCode=500,
                status=ResponseStatus.failed,
                message=f"An error occurred when trying to create bookmark category {title}",
                response=str(e)
            )

    async def delete(self, uuid: str) -> ResponseModel[str]:
        try:
            category: BookMarkCategory | None = await self.get_one_by_uuid(uuid)

            if category is not None:
                await category.delete()

                return ResponseModel(
                    message=f"Bookmark category {uuid} deleted successfully",
                    statusCode=200,
                    status=ResponseStatus.success
                )
            else:
                return ResponseModel(
                    message=f"Bookmark category {uuid} does not exist",
                    statusCode=404,
                    status=ResponseStatus.failed
                )
        except Exception as e:
            return ResponseModel(
                statusCode=500,
                status=ResponseStatus.failed,
                message=f"An error occurred when trying to delete bookmark category {uuid}",
                response=str(e)
            )

    async def add_bookmark_to_category(self, body: BookmarkCategoryCreateDto) -> ResponseModel[str]:
        try:
            bookmark_exist: bool = await self.bookmark_repository.exist_by_uuid(body.bookmark_uuid)
            if bookmark_exist:
                bookmark_category_exist: bool = await self.exist_by_uuid(body.category_uuid)

                print(bookmark_category_exist)

                if bookmark_category_exist:

                    get_category = await self.get_one_by_uuid(body.category_uuid)
                    get_bookmark = await self.bookmark_repository.get_by_uuid(body.bookmark_uuid)

                    print(get_bookmark)
                    print(get_category)

                    if get_bookmark is not None and get_category is not None:
                        data = BookMarkModelCategory(
                            category=get_category,
                            bookmark=get_bookmark
                        )

                        await BookMarkModelCategory.save(data)
                        return ResponseModel(
                            message=f"Bookmark {body.bookmark_uuid} added to category {body.category_uuid} successfully",
                            statusCode=200,
                            status=ResponseStatus.success
                        )
                    return ResponseModel(
                        message=f"Bookmark {body.bookmark_uuid} or Category {body.category_uuid} does not exist",
                        statusCode=404,
                        status=ResponseStatus.failed
                    )

            return ResponseModel(
                message=f"Bookmark {body.bookmark_uuid} does not exist",
                statusCode=404,
                status=ResponseStatus.failed
            )
        except Exception as e:
            return ResponseModel(
                statusCode=500,
                status=ResponseStatus.failed,
                message=f"""
                        An error occurred when trying add 
                        bookmark {body.bookmark_uuid}
                        in category {body.category_uuid}
                        """,
                response=str(e)
            )

    async def exist_by_title(self, title: str) -> bool:
        category = await BookMarkCategory.filter(title=title).first()
        return category is not None

    async def exist_by_uuid(self, uuid: str) -> bool:
        category = await BookMarkCategory.filter(uuid=uuid).first()
        return category is not None

    async def get_one_by_uuid(self, uuid: str) -> BookMarkCategory | None:
        return await BookMarkCategory.get_or_none(uuid=uuid)

