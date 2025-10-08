from tortoise import fields
from tortoise.models import Model

class Genre(Model):
    uuid = fields.IntField(pk=True)
    name = fields.CharField(unique=True, max_length=255)
    created_at = fields.DateField(auto_now=True)
    updated_at = fields.DateField(auto_now=True)