from app.core import ResponseModel, ResponseStatus
from app.dto import CreateBookMarkDto, DeleteBookMarkDto
from tortoise.transactions import in_transaction

from common.models import BookMarkModel


class BookMarkRepository:

    async def create(self, body: CreateBookMarkDto) -> ResponseModel[str]:
        """
        Create a new bookmark
        :param body:
        :return:
        """

        """ TODO : Verify if given user and video exists  """
        try:
            async with in_transaction() as conn:
                """ Insert the data """
                db_data: BookMarkModel = BookMarkModel(
                    user_uuid=body.user_id,
                    video_uuid=body.video_id
                )
                await db_data.save(using_db=conn)
            return ResponseModel(response="ok", statusCode=201, status=ResponseStatus.success)
        except Exception as e:
            return ResponseModel(response=str(e), statusCode=500, status=ResponseStatus.failed)

    async def delete(self, data: DeleteBookMarkDto) -> ResponseModel[str]:
        try:
            async with in_transaction() as conn:
                bookmark = await BookMarkModel.filter(uuid=data.uuid).using_db(conn).first()

                if not bookmark:
                    return ResponseModel(
                        message=f"BookMark {data.uuid} does not exist",
                        statusCode=404,
                        status=ResponseStatus.failed
                    )

                await bookmark.delete(using_db=conn)

                return ResponseModel(
                    message=f"BookMark {data.uuid} deleted successfully",
                    statusCode=200,
                    status=ResponseStatus.success
                )
        except Exception as e:
            return ResponseModel(
                response=str(e),
                message=f"An error occurred when deleting bookmark {data.uuid}",
                statusCode=500,
                status=ResponseStatus.failed
            )

    async def get_by_uuid(self, uuid: str) -> BookMarkModel | None:
        data = await BookMarkModel.get_or_none(uuid=uuid)
        return data

    async def exist_by(self, data: CreateBookMarkDto) -> bool:
        data = await BookMarkModel.filter(user_uuid = data.user_id, video_uuid = data.video_id).first()
        return data is not None

    async def exist_by_uuid(self, uuid: str) -> bool:
        data = await BookMarkModel.filter(uuid=uuid).first()
        return data is not None
