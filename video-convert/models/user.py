from tortoise import fields
from tortoise.models import Model
import uuid
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    pseudo = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=128)
    role = fields.CharEnumField(UserRole, default=UserRole.USER)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.pseudo
