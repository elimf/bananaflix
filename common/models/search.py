from tortoise import fields
from tortoise.models import Model
import uuid

class Search(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    term = fields.CharField(max_length=255)   # le texte de recherche (titre ou genre)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "searches"
