from tortoise import fields
from tortoise.models import Model
import uuid

from common.models import Video


class Stat(Model):
    uuid = fields.UUIDField(pk=True, default=uuid.uuid4)
    video: fields.ForeignKeyRelation[Video] = fields.ForeignKeyField(
        "models.Video", related_name="stats", on_delete=fields.CASCADE
    )

    add_bookmark = fields.IntField(default=0)
    remove_bookmark = fields.IntField(default=0)
    as_view = fields.IntField(default=0)
    stop = fields.IntField(default=0)
    play = fields.IntField(default=0)
    pause = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
