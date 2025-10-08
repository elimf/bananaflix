import os
import uvicorn
from fastapi import FastAPI, Response
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from typing import AsyncIterator
import redis.asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from common.models import Video
from common.utils.search_cache import search_key_builder

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Lifespan pour initialiser Redis avant le démarrage
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis_client = aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8"
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="search-cache")
    app.state.redis_client = redis_client
    yield

app = FastAPI(title="Search Service", lifespan=lifespan)

# CORS pour React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_KEY = "user_searches"
@app.get("/search")
@cache(expire=60, key_builder=search_key_builder)
async def search(title: str | None = None, genre: str | None = None, response: Response = None):
    query = Video.all().prefetch_related("genre")
    if title:
        query = query.filter(title__icontains=title)
    if genre:
        genres = [g.strip() for g in genre.split(",") if g.strip()]
        if genres:
            query = query.filter(genre__name__in=genres)

    results = await query.all()

    if title or genre:
        redis_client = app.state.redis_client
        search_term = title or genre
        await redis_client.lpush(USER_KEY, search_term)
        await redis_client.ltrim(USER_KEY, 0, 9)
        await redis_client.expire(USER_KEY, 60)
    return results

@app.get("/suggestions")
async def suggestions():
    redis_client = app.state.redis_client
    recent_searches = await redis_client.lrange(USER_KEY, 0, -1)
    return list(dict.fromkeys(recent_searches))

register_tortoise(
    app,
    db_url="postgres://banana:banana@bananaflix-chart-db:5432/banana-db",
    modules={"models": ["common.models"]},
    generate_schemas=False,
    add_exception_handlers=True,
)
