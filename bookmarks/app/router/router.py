from fastapi import APIRouter
from app.core import ResponseModel
from app.dto import CreateBookMarkDto, BookmarkCategoryCreateDto
from app.service import BookMarkService, BookMarkCategoryService

router = APIRouter()

bookmark_service = BookMarkService()
bookmark_category_service = BookMarkCategoryService()


@router.delete("/bookmarks")
async def delete(uuid: str) -> ResponseModel[str]:
    return await bookmark_service.delete(uuid)


@router.post("/bookmarks")
async def create(body: CreateBookMarkDto) -> ResponseModel[str]:
    return await bookmark_service.create(body)


@router.post("/bookmarks/category")
async def create_bookmark_category(title: str) -> ResponseModel[str]:
    return await bookmark_category_service.create(title)


@router.delete("/bookmarks/category")
async def delete(uuid: str) -> ResponseModel[str]:
    return await bookmark_category_service.delete(uuid)


@router.post("/bookmarks/category/add")
async def add_bookmark_to_category(body: BookmarkCategoryCreateDto) -> ResponseModel[str]:
    return await bookmark_category_service.add_bookmark_to_category(body)
