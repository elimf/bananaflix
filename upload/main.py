from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid, aiofiles, os, httpx
from contextlib import asynccontextmanager

UPLOAD_DIR = "storage/uploads"
CONVERT_SERVICE_URL = os.getenv("CONVERT_SERVICE_URL", "http://video-convert-service:8002/convert")

@asynccontextmanager
async def lifespan(app: FastAPI):
    timeout = httpx.Timeout(5.0, connect=5.0, read=60.0, write=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        app.state.http_client = client
        yield

os.makedirs(UPLOAD_DIR, exist_ok=True)
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    duration: int = Form(...),
    genre_id: int = Form(...),
    generate_trailer: bool = Form(False)
):
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        async with aiofiles.open(file_path, "wb") as out_f:
            while True:
                chunk = await file.read(1024 * 1024) # 1MB
                if not chunk:
                    break
                await out_f.write(chunk)
        
        client: httpx.AsyncClient = app.state.http_client
        with open(file_path, "rb") as video_file:
                response = await client.post(
                    CONVERT_SERVICE_URL,
                    data={
                        "title": title,
                        "description": description,
                        "duration": duration,
                        "genre_id": genre_id,
                        "generate_trailer": str(generate_trailer).lower(),
                    },
                    files={"file": (unique_filename, video_file, file.content_type)},
                )
        
        response.raise_for_status()
        
        return {
            "message": "Upload and conversion started",
            "response": response.json()
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Conversion service error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Unable to connect to conversion service: {e}")
