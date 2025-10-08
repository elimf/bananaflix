import asyncio
import logging
from contextlib import asynccontextmanager
import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, HTTPException
import paho.mqtt.client as mqtt
from typing import Optional
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from common.models.stats import Stat
from common.utils.stats_cache import request_key_builder
from common.utils.mqtt_worker import on_connect, on_disconnect, on_message, MQTT_HOST, MQTT_PORT, message_queue, REDIS_HOST, \
    REDIS_PORT
from stats_services import update_stats

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

mqtt_client: Optional[mqtt.Client] = None
main_loop: Optional[asyncio.AbstractEventLoop] = None

async def process_queue():
    """Boucle asynchrone qui lit la queue et met à jour la DB"""
    while True:
        payload = await asyncio.to_thread(message_queue.get)  # lit sans bloquer la loop
        await update_stats(payload)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_client
    # Startup
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message

    try:
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
        mqtt_client.loop_start()
        logging.info("MQTT client started")
    except Exception as e:
        logging.error(f"Failed to start MQTT client: {e}")
        mqtt_client = None

    # Redis cache
    redis_client = redis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        encoding="None",
        decode_responses=False
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    task = asyncio.create_task(process_queue())
    yield

    # Shutdown
    task.cancel()
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logging.info("MQTT client stopped")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_metadata():
    return {
        "Hello": "Stats"
    }


@app.get("/stats/video/{video_id}")
@cache(expire=60*5, key_builder=request_key_builder)
async def get_video_stats(video_id: str):
    stat = await Stat.get_or_none(video_id=video_id).prefetch_related("video")
    if not stat:
        raise HTTPException(status_code=404, detail="No stats for this video")
    return {
        "video": {
            "id": stat.video.id,
            "title": stat.video.title,
            "description": stat.video.description,
            "duration": stat.video.duration,
            "status": stat.video.status,
            "output_file": stat.video.output_file,
            "trailer_file": stat.video.trailer_file,
            "trailer_status": stat.video.trailer_status,
        },
        "stats": {
            "add_bookmark": stat.add_bookmark,
            "remove_bookmark": stat.remove_bookmark,
            "as_view": stat.as_view,
            "play": stat.play,
            "stop": stat.stop,
            "pause": stat.pause,
        }
    }


@app.get("/stats/global")
@cache(expire=60*5, key_builder=request_key_builder)
async def get_global_stats():
    stats = await Stat.all().prefetch_related("video")
    result = []
    for stat in stats:
        if stat.video: 
            result.append({
                "video": {
                    "id": stat.video.id,
                    "title": stat.video.title,
                    "description": stat.video.description,
                    "duration": stat.video.duration,
                    "status": stat.video.status,
                    "output_file": stat.video.output_file,
                    "trailer_file": stat.video.trailer_file,
                    "trailer_status": stat.video.trailer_status,
            },
                "stats": {
                    "add_bookmark": stat.add_bookmark,
                    "remove_bookmark": stat.remove_bookmark,
                    "as_view": stat.as_view,
                    "play": stat.play,
                    "stop": stat.stop,
                    "pause": stat.pause,
                }
            })
    return result

register_tortoise(
    app,
    db_url="postgres://banana:banana@bananaflix-chart-db:5432/banana-db", # Remplacez par postgres://banana:banana@localhost:5432/banana-db si vous ne dockerisez pas upload et video-convert les gars
    modules={"models": ["common.models"]},
    generate_schemas=False,
    add_exception_handlers=True
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
