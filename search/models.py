from enum import Enum

from tortoise.models import Model
from tortoise import fields




class Genre(Model):
    uuid = fields.IntField(pk=True)
    name = fields.CharField(unique=True, max_length=255)
    created_at = fields.DateField(auto_now=True)
    updated_at = fields.DateField(auto_now=True)

class Video(Model):
    title = fields.CharField(max_length=255)
    duration = fields.IntField()
    genre = fields.ForeignKeyField("models.Genre")
    status = fields.BooleanField(default=True)
