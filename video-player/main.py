import enum
import os

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Query
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse,Response
from tortoise.contrib.fastapi import register_tortoise

from common.models.video_user import Quality
from common.models import VideoUser, Video


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(
    app,
    db_url="postgres://banana:banana@bananaflix-chart-db:5432/banana-db",
    modules={"models": ["common.models"]},
    generate_schemas=False,
    add_exception_handlers=True,
)

class StatType(str, enum.Enum):
        play = "play"
        stop = "stop"
        pause = "pause"

class SaveProgressApiRequest(BaseModel):
    video_user_info : int
    progress_duration : int

def start_or_resume_video(request: Request, file_path : str):
    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("range")

    def iter_file(start: int, end: int):
        with open(file_path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            chunk_size = 1024 * 1024
            while remaining > 0:
                read_length = min(chunk_size, remaining)
                data = f.read(read_length)
                if not data:
                    break
                yield data
                remaining -= len(data)

    if range_header:
        bytes_range = range_header.strip().lower().replace("bytes=", "").split("-")
        try:
            start = int(bytes_range[0])
            end = int(bytes_range[1]) if bytes_range[1] else file_size - 1
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Range header")

        if start >= file_size or end >= file_size:
            return Response(status_code=416, headers={
                "Content-Range": f"bytes */{file_size}"
            })

        content_length = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": "video/mp4",
        }

        return StreamingResponse(iter_file(start, end), status_code=206, headers=headers)

    else:
        headers = {
            "Content-Length": str(file_size),
            "Content-Type": "video/mp4",
            "Accept-Ranges": "bytes",
        }
        return StreamingResponse(iter_file(0, file_size - 1), headers=headers)

@app.get("/video-info-user/")
async def get_info_video_for_user(video_id: int = Query(..., description="ID de l'artiste"), user_id: str = Query(..., description="ID de l'artiste"), quality: Quality = Query(..., description="ID de l'artiste")):
    if video_id is None and user_id is None:
        raise HTTPException(status_code=400)
    user_info_video = await VideoUser.get_or_none(video_id=video_id, user_id=user_id)
    video = await Video.get_or_none(id=video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found bbb")
    if user_info_video is None:
        user_info_video = await VideoUser.create(
            video=video,
            user_id=user_id,
            progress_duration=0,
            status=VideoUser.Status.progress,
            quality= quality
        )

    if user_info_video.quality != quality:
        user_info_video.quality = quality


    return {"user_info_video" : user_info_video, "video" : video}

@app.get("/videos/{video_id}")
async def stream_video(
        request: Request,
        video_id: str,
        quality: str = Query("720p")
):
    video = await Video.get_or_none(id=video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")

    video_user = await VideoUser.get_or_none(video=video)
    resume_progress = 0
    if video_user:
        resume_progress = video_user.progress_duration
    else:
        await VideoUser.create(video=video, progress_duration=0, status=VideoUser.Status.progress)

    video_path: str = video.file_path 

    if video.output_file is not None and video.status == "done":
        if video.qualities and quality in video.qualities:
            video_path = video.qualities[quality]
        else:
            raise HTTPException(status_code=400, detail=f"Quality '{quality}' not available")

    return start_or_resume_video(request, video_path)


@app.post("/videos/progress")
async def save_progression (body: SaveProgressApiRequest):
    user_info_video = await VideoUser.get_or_none(id=body.video_user_info)
    if user_info_video is None:
        raise HTTPException(status_code=404, detail="Not find video user info")
    user_info_video.progress_duration = body.progress_duration
    await user_info_video.save()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)

