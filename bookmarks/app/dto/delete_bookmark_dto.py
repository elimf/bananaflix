from pydantic import BaseModel


class DeleteBookMarkDto(BaseModel):
    uuid: str
