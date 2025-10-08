from pydantic import BaseModel


class CreateBookMarkDto(BaseModel):
    user_id: str
    video_id: int
