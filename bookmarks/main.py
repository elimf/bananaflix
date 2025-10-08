from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.router import router

app = FastAPI(title="BananaFlix - Bookmarks")

app.include_router(router)

register_tortoise(
    app,
    db_url="postgres://banana:banana@bananaflix-db:5432/banana-db", # Remplacez par postgres://banana:banana@localhost:5432/banana-db si vous ne dockerisez pas upload et video-convert les gars
    modules={"models": ["common.models"]},
    generate_schemas=False,
    add_exception_handlers=True
)
