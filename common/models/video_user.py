import enum

from tortoise import Model, fields


class Quality(str, enum.Enum):
    SD = "360p"
    HD = "720p"
    FHD = "1080p"

class VideoUser(Model):
        class Status(str, enum.Enum):
            progress = "progress",
            finish = "finish"
        video = fields.ForeignKeyField(
            model_name= "models.Video",
        )
        user = fields.ForeignKeyField(model_name= "models.User")
        progress_duration = fields.IntField()
        status = fields.CharEnumField(enum_type=Status, default=Status.progress)
        created_at = fields.DatetimeField(auto_now_add=True)
        updated_at = fields.DatetimeField(auto_now=True)
        quality = fields.CharEnumField(enum_type=Quality, default=Quality.HD)


