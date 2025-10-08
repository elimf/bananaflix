from tortoise import fields
from tortoise.models import Model

class Video(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    duration = fields.IntField()
    genre = fields.ForeignKeyField("models.Genre", related_name="videos")
    file_path = fields.CharField(max_length=500, null=True)
    output_file = fields.CharField(max_length=500, null=True)
    trailer_file = fields.CharField(max_length=500, null=True)
    status = fields.CharField(max_length=20, default="pending")
    trailer_status = fields.CharField(max_length=20, null=True, default="none")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.title
