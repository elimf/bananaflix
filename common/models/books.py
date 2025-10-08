from tortoise.models import Model
from tortoise import fields
import uuid


class BookMarkModel(Model):
    uuid = fields.UUIDField(primary_key=True, default=uuid.uuid4())
    user_uuid = fields.UUIDField()
    video_uuid = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    categories = fields.ManyToManyField(
    "models.BookMarkCategory",
    related_name="bookmarks",
    through="bookmarkmodelcategory",
    forward_key="book_mark_id",
    backward_key="category_id"
)



class BookMarkCategory(Model):
    uuid = fields.UUIDField(primary_key=True, default=uuid.uuid4())
    title = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class BookMarkModelCategory(Model):
    uuid = fields.UUIDField(primary_key=True, default=uuid.uuid4())
    bookmark = fields.ForeignKeyField("models.BookMarkModel", related_name="bookmark_links")
    category = fields.ForeignKeyField("models.BookMarkCategory", related_name="category_links")
    created_at = fields.DatetimeField(auto_now_add=True)
