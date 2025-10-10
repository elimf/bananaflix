import json
import logging
from contextlib import asynccontextmanager
import redis.asyncio as redis
import httpx
from fastapi import FastAPI, Depends, HTTPException, Query, Response, UploadFile, File, Form
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import paho.mqtt.client as mqtt
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import StreamingResponse
from tortoise.contrib.fastapi import register_tortoise
from prometheus_client import start_http_server, Counter, generate_latest, CONTENT_TYPE_LATEST
from common.models import Video, Genre
from common.models.books import BookMarkModel
from common.utils.stats_cache import request_key_builder
from config import CONVERTER_SERVICE_URL, STATS_SERVICE_URL, REDIS_HOST, REDIS_PORT, MQTT_HOST, MQTT_PORT, PLAYER_VIDEO_URL,UPLOAD_SERVICE_URL,BOOKMARK_SERVICE_URL
from dto import UserCreate, UserOut, Token, LoginRequest, GenreCreate, CreateBookMarkDto, BookmarkCategoryCreateDto, \
    DeleteBookmarkDto
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from common.models.user import User
from common.response_model import ResponseModel, ResponseStatus

mqtt_client_main = None
@asynccontextmanager
async def lifespan(_: FastAPI):
    global mqtt_client_main
    mqtt_client_main = mqtt.Client()
    try:
        mqtt_client_main.connect(MQTT_HOST, MQTT_PORT, 60)
        mqtt_client_main.loop_start()
        logging.info("MQTT client connected and loop started")
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker: {e}")
        mqtt_client_main = None

    # Redis cache
    redis_client = redis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        encoding=None,
        decode_responses=False
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-main-cache")

    yield
    if mqtt_client_main:
        mqtt_client_main.loop_stop()
        mqtt_client_main.disconnect()
        logging.info("MQTT client stopped cleanly")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUESTS = Counter("main_service_requests_total", "Total requests to main-service")
ERRORS = Counter("main_service_errors_total", "Total number of errors occurred")
VIDEO_UPLOADS = Counter("video_uploads_total", "Total number of uploaded videos")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
@app.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    user_exists = await User.get_or_none(pseudo=user.pseudo)
    if user_exists:
        raise HTTPException(status_code=400, detail="Pseudo already taken")
    hashed_pwd = get_password_hash(user.password)
    new_user = await User.create(
        pseudo=user.pseudo,
        password=hashed_pwd,
    )
    return UserOut(
        id=new_user.id,
        pseudo=new_user.pseudo,
    )

@app.post("/login", response_model=Token)
async def login(data: LoginRequest):
    REQUESTS.inc()
    user = await User.get_or_none(pseudo=data.pseudo)
    if not user or not verify_password(data.password, user.password):
        ERRORS.inc()
        raise HTTPException(status_code=401, detail="Incorrect pseudo or password")
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "pseudo": user.pseudo
        },
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/stats/video/{video_id}")
@cache(expire=60*5, key_builder=request_key_builder)
async def get_video_stats(video_id: str):
    REQUESTS.inc()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{STATS_SERVICE_URL}/stats/video/{video_id}")
        except httpx.RequestError as e:
            ERRORS.inc()
            raise HTTPException(status_code=503, detail=f"Stats service unreachable: {str(e)}")

    if response.status_code == 404:
        ERRORS.inc()
        raise HTTPException(status_code=404, detail="No stats for this video")

    if response.status_code != 200:
        ERRORS.inc()
        raise HTTPException(status_code=response.status_code, detail="Error from stats service")

    return response.json()


@app.get("/stats/global")
@cache(expire=60*5, key_builder=request_key_builder)
async def get_global_stats():
    REQUESTS.inc()
    async with httpx.AsyncClient() as client:
        try:
            print(STATS_SERVICE_URL)
            response = await client.get(f"{STATS_SERVICE_URL}/stats/global")
        except httpx.RequestError as e:
            ERRORS.inc()
            raise HTTPException(status_code=503, detail=f"Stats service unreachable: {str(e)}")

    if response.status_code != 200:
        ERRORS.inc()
        raise HTTPException(status_code=response.status_code, detail="Error from stats service")

    return response.json()

@app.get("/videos/{video_id}")
async def get_video(request : Request, video_id: str, quality: str = Query(..., description="Résolution de la vidéo")):
    REQUESTS.inc()
    range_header = request.headers.get("range")  # récupère le Range du client

    headers = {}
    if range_header:
        headers["range"] = range_header
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PLAYER_VIDEO_URL}/videos/{video_id}?quality={quality}",
            headers=headers,
            timeout=None
        )

        if resp.status_code == 404:
            ERRORS.inc()
            raise HTTPException(status_code=404, detail="Video not found")

        content_length = resp.headers.get("Content-Length")
        content_range = resp.headers.get("Content-Range")
        content_type = resp.headers.get("Content-Type", "video/mp4")
        accept_ranges = resp.headers.get("Accept-Ranges", "bytes")

        return StreamingResponse(
            resp.aiter_bytes(),
            status_code=resp.status_code,
            headers={
                "Content-Length": content_length,
                "Content-Range": content_range,
                "Content-Type": content_type,
                "Accept-Ranges": accept_ranges,
            }
        )
@app.get("/video-info-user/",)
async def get_info_video_for_user(video_id: int = Query(..., description="ID de l'artiste"), quality: str = Query(..., description="ID de l'artiste"),current_user: User = Depends(get_current_user)):
    REQUESTS.inc()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PLAYER_VIDEO_URL}/video-info-user/?video_id={video_id}&user_id={current_user.id}&quality={quality}")
        except httpx.RequestError as e:
            ERRORS.inc()
            raise HTTPException(status_code=503, detail=f"Player service unreachable: {str(e)}")
    return response.json()


@app.post("/videos/stats")
async def update_video_stats(request: Request, current_user: User = Depends(get_current_user)):
    REQUESTS.inc()
    data = await request.json()
    video_id = data.get("video_id")
    event_stat = data.get("event_stat")
    if not video_id or not event_stat:
        ERRORS.inc()
        raise HTTPException(status_code=400, detail="Missing video_id or event_stat")
    if mqtt_client_main:
        mqtt_client_main.publish("metadata/stats-analyzed",payload=json.dumps({"video_uuid": video_id, "type": event_stat}))
@app.post("/videos/progress")
async def save_progression (request: Request):
    REQUESTS.inc()
    data = await request.json()
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{PLAYER_VIDEO_URL}/videos/progress", json=data)
        except httpx.RequestError as e:
            ERRORS.inc()
            raise HTTPException(status_code=503, detail=f"Player service unreachable: {str(e)}")
@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    duration: int = Form(...),
    genre_id: int = Form(...),
    generate_trailer: bool = Form(False)

):
    REQUESTS.inc()
    try:
        timeout = httpx.Timeout(10.0, connect=10.0, read=300.0, write=300.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            form_data = {
                "title": title,
                "description": description,
                "duration": str(duration),
                "genre_id": str(genre_id),
                "generate_trailer": str(generate_trailer).lower(),
            }
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(
                f"{UPLOAD_SERVICE_URL}/upload",
                data=form_data,
                files=files
            )

        if response.status_code != 200:
            ERRORS.inc()
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Upload service error: {response.text}"
            )
        VIDEO_UPLOADS.inc()
        return response.json()

    except httpx.RequestError as e:
        ERRORS.inc()
        raise HTTPException(status_code=503, detail=f"Upload service unreachable: {str(e)}")

@app.get("/videos")
async def get_video():
    REQUESTS.inc()
    try:
        timeout = httpx.Timeout(10.0, connect=10.0, read=300.0, write=300.0)
        async with httpx.AsyncClient(timeout=timeout) as client:

            response = await client.get(
                f"{CONVERTER_SERVICE_URL}/videos",
            )

        if response.status_code != 200:
            ERRORS.inc()
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Converter service error: {response.text}"
            )

        return response.json()

    except httpx.RequestError as e:
        ERRORS.inc()
        raise HTTPException(status_code=503, detail=f"Converter service unreachable: {str(e)}")

@app.get("/genres")
async def get_genres():
    REQUESTS.inc()
    genres = await Genre.all()
    return [
        {
            "uuid": g.uuid,
            "name": g.name,
        }
        for g in genres
    ]


@app.post("/genres")
async def create_genre(genre: GenreCreate):
    REQUESTS.inc()
    existing = await Genre.get_or_none(name=genre.name)
    if existing:
        ERRORS.inc()
        raise HTTPException(status_code=400, detail="Genre already exists")
    new_genre = await Genre.create(name=genre.name)
    return {
        "uuid": new_genre.uuid,
        "name": new_genre.name,
        "created_at": new_genre.created_at,
        "updated_at": new_genre.updated_at
    }

@app.post("/bookmarks")
async def add_bookmark(body: CreateBookMarkDto):
    REQUESTS.inc()
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "user_id": body.user_id,
                "video_id": body.video_id,
            }
            response = await client.post(
                f"{BOOKMARK_SERVICE_URL}/bookmarks",
                json=payload  # <-- envoi JSON, pas form-data
            )
            if mqtt_client_main:
                mqtt_client_main.publish("metadata/stats-analyzed",payload=json.dumps({"video_uuid": body.video_id, "type": "add_bookmark"}))
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json")
            )

        except Exception as e:
            ERRORS.inc()
            return Response(content=str(e), status_code=500)

@app.delete("/bookmarks")
async def delete_bookmark(body: DeleteBookmarkDto):
    REQUESTS.inc()
    async with httpx.AsyncClient() as client:
        try:
            book = await BookMarkModel.get_or_none(uuid=body.uuid)
            if not book:
                ERRORS.inc()
                return Response(
                    content=json.dumps({"error": "Bookmark not found"}),
                    status_code=404,
                    media_type="application/json"
                )

            response = await client.delete(
                f"{BOOKMARK_SERVICE_URL}/bookmarks",
                params={"uuid": body.uuid}
            )

            if mqtt_client_main:
                mqtt_client_main.publish(
                    "metadata/stats-analyzed",
                    payload=json.dumps({
                        "video_uuid": book.video_uuid,
                        "type": "remove_bookmark"
                    })
                )

            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json")
            )

        except Exception as e:
            ERRORS.inc()
            return Response(
                content=json.dumps({"error": str(e)}),
                status_code=500,
                media_type="application/json"
            )


@app.get("/bookmarks/user")
async def get_user_bookmark_videos(current_user: User = Depends(get_current_user)):
    try:
        REQUESTS.inc()
        bookmarks = await BookMarkModel.filter(user_uuid=current_user.id)
        if not bookmarks:
            ERRORS.inc()
            return Response(
                content=json.dumps([]),
                status_code=200,
                media_type="application/json"
            )

        result = []
        for b in bookmarks:
            video = await Video.get_or_none(id=b.video_uuid)
            if video:
                result.append({
                    "bookmark_uuid": str(b.uuid),
                        "id": video.id,
                        "title": video.title,
                        "description": video.description,
                        "duration": video.duration,
                        "status": video.status,
                        "output_file": video.output_file,
                        "trailer_file": video.trailer_file,
                        "trailer_status": video.trailer_status
                })

        return Response(
            content=json.dumps(result),
            status_code=200,
            media_type="application/json"
        )

    except Exception as e:
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json"
        )
register_tortoise(
    app,
    db_url="postgres://banana:banana@bananaflix-chart-db:5432/banana-db", # Remplacez par postgres://banana:banana@localhost:5432/banana-db si vous ne dockerisez pas upload et video-convert les gars
    modules={"models": ["common.models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
