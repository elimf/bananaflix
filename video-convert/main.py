from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from converter.worker import handle_video_conversion, executor, run_async_from_thread, sanitize_filename
from converter.ffmpeg_utils import extract_trailer
import uuid, os, aiofiles, asyncio, logging, time
from common.models.video import Video
from tortoise import Tortoise
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
UPLOAD_DIR = "storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(
        db_url="postgres://banana:banana@bananaflix-chart-db:5432/banana-db",
        modules={"models": ["common.models"]}
    )
    await Tortoise.generate_schemas()
    logger.info("Tortoise ORM initialized")
    
    yield

    executor.shutdown(wait=True, cancel_futures=False)
    logger.info("ThreadPool executor shut down")
    
    await Tortoise.close_connections()
    logger.info("Tortoise ORM closed")

app = FastAPI(lifespan=lifespan)
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

@app.post("/convert")
async def convert(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    duration: int = Form(...),
    genre_id: int = Form(...),
    generate_trailer: str = Form("false")
):
    try:
        gen_trailer = generate_trailer.lower() == "true"
        safe_title = sanitize_filename(title)
        file_ext = os.path.splitext(file.filename)[1]
        
        timestamp = int(time.time())
        filename = f"{timestamp}_{safe_title}{file_ext}"
        input_path = os.path.join(UPLOAD_DIR, filename)

        async with aiofiles.open(input_path, "wb") as out_f:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                await out_f.write(chunk)

        result = await handle_video_conversion(
            input_path=input_path,
            title=title,
            description=description,
            duration=duration,
            genre_id=genre_id,
            generate_trailer=gen_trailer,
        )

        return result 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/videos/{video_id}/generate-trailer", status_code=202)
async def generate_trailer_endpoint(video_id: int):
    video = await Video.get_or_none(id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if not video.output_file:
        raise HTTPException(status_code=400, detail="Video has not been converted yet")
    if video.trailer_file:
        return {"message": "Trailer already exists", "trailer_path": video.trailer_file}

    await Video.filter(id=video_id).update(trailer_status="processing")

    trailer_path = video.output_file.replace(".mp4", "_trailer.mp4")

    def extract_and_update(video_id, input_path, trailer_path, loop):
        try:
            extract_trailer(input_path, trailer_path)
            update_coro = Video.filter(id=video_id).update(
                trailer_status="done",
                trailer_file=trailer_path
            )
            run_async_from_thread(update_coro, loop)
        except Exception as e:
            update_coro = Video.filter(id=video_id).update(
                trailer_status="failed"
            )
            run_async_from_thread(update_coro, loop)
            logger.error(f"Trailer generation failed for {video_id}: {e}", exc_info=True)

    loop = asyncio.get_running_loop()
    executor.submit(extract_and_update, video.id, video.output_file, trailer_path, loop)
    return {"message": "Trailer generation started", "trailer_path": trailer_path}

@app.get("/videos")
async def get_all_videos(
    skip: int = 0,
    limit: int = 100,
    status: str = None
):
    query = Video.all()
    
    if status:
        query = query.filter(status=status)
    
    videos = await query.offset(skip).limit(limit).prefetch_related('genre')
    
    total = await Video.all().count()
    
    results = []
    for video in videos:
        results.append({
            "id": video.id,
            "title": video.title,
            "description": video.description,
            "duration": video.duration,
            "genre": {
                "id": video.genre.uuid,
                "name": video.genre.name
            } if video.genre else None,
            "status": video.status,
            "output_file": video.output_file,
            "qualities": video.qualities,
            "trailer_file": video.trailer_file,
            "trailer_status": video.trailer_status,
            "created_at": video.created_at.isoformat() if video.created_at else None,
            "updated_at": video.updated_at.isoformat() if video.updated_at else None
        })
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "videos": results
    }

@app.get("/videos/{video_id}")
async def get_video(video_id: int, request: Request):
    video = await Video.get_or_none(id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {
        "id": video.id,
        "title": video.title,
        "description": video.description,
        "duration": video.duration,
        "status": video.status,
        "output_file": video.output_file,
        "trailer_file": video.trailer_file,
        "trailer_status": video.trailer_status
    }