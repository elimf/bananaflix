from app.repository import BookMarkRepository
from app.dto import CreateBookMarkDto, DeleteBookMarkDto
from app.core.response_model import ResponseModel, ResponseStatus


class BookMarkService:

    def __init__(self):
        self.bookmark_repository = BookMarkRepository()

    async def create(self, body: CreateBookMarkDto) -> ResponseModel[str]:
        exist: bool = await self.bookmark_repository.exist_by(body)
        if exist:
            return ResponseModel(
                message=f"BookMark for video {body.video_id} already exist",
                statusCode=200,
                status=ResponseStatus.success
            )
        return await self.bookmark_repository.create(body)

    async def delete(self, uuid: str) -> ResponseModel[str]:
        data = DeleteBookMarkDto(uuid = uuid)
        return await self.bookmark_repository.delete(data)
