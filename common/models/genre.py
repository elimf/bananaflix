from tortoise import fields
from tortoise.models import Model

class Genre(Model):
    uuid = fields.IntField(pk=True)
    name = fields.CharField(unique=True, max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)