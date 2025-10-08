import os, asyncio, logging, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from converter.ffmpeg_utils import convert_video_with_resolution, extract_trailer
from common.models.video import Video
from common.models.genre import Genre

executor = ThreadPoolExecutor(max_workers=8)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONVERTED_DIR = "storage/converted"
os.makedirs(CONVERTED_DIR, exist_ok=True)

def run_async_from_thread(coro, loop):
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=30)

QUALITIES = {
    "360p": 360,
    "720p": 720,
    "1080p": 1080,
}

def sanitize_filename(title: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*]', '_', title)
    safe = re.sub(r'\s+', '_', safe.strip())
    safe = safe[:100]
    return safe

async def update_video_status(video_id: int, status: str, output_file: str = None, 
                              qualities: dict = None, trailer_file: str = None, 
                              trailer_status: str = None):
    update_data = {"status": status}
    if output_file is not None:
        update_data["output_file"] = output_file
    if qualities is not None:
        update_data["qualities"] = qualities
    if trailer_file is not None:
        update_data["trailer_file"] = trailer_file
    if trailer_status is not None:
        update_data["trailer_status"] = trailer_status
    
    await Video.filter(id=video_id).update(**update_data)

def convert_single_quality(input_path: str, output_path: str, resolution: int, label: str):
    try:
        logger.info(f"Starting conversion for {label}")
        convert_video_with_resolution(input_path, output_path, resolution)
        logger.info(f"Completed conversion for {label}")
        return label, output_path, None
    except Exception as e:
        logger.error(f"Failed conversion for {label}: {e}")
        return label, None, str(e)

def convert_and_update(video_id: int, input_path: str, base_output_path: str, generate_trailer: bool, loop):
    try:
        outputs = {}
        failed = {}
        
        futures_map = {}
        for label, res in QUALITIES.items():
            base_without_ext = os.path.splitext(base_output_path)[0]
            out_path = f"{base_without_ext}_{label}.mp4"

            future = executor.submit(convert_single_quality, input_path, out_path, res, label)
            futures_map[future] = label
        
        for future in as_completed(futures_map):
            label, out_path, error = future.result()
            if error:
                failed[label] = error
            else:
                outputs[label] = out_path
        
        if "720p" not in outputs:
            raise Exception(f"Critical: 720p conversion failed. Failures: {failed}")
        
        trailer_path = None
        trailer_status = "none"
        if generate_trailer:
            try:
                trailer_path = base_output_path.replace(".mp4", "_trailer.mp4")
                extract_trailer(outputs["720p"], trailer_path)
                trailer_status = "done"
                logger.info(f"Trailer generated for video {video_id}")
            except Exception as e:
                logger.error(f"Trailer generation failed: {e}")
                trailer_status = "failed"

        logger.info(f"Updating video {video_id} in database...")
        logger.info(f"  Status: {'done' if not failed else 'partial'}")
        logger.info(f"  Output file: {outputs['720p']}")
        logger.info(f"  Qualities: {outputs}")
        logger.info(f"  Trailer: {trailer_path} ({trailer_status})")
        
        try:
            run_async_from_thread(
                update_video_status(
                    video_id=video_id,
                    status="done" if not failed else "partial",
                    output_file=outputs["720p"],
                    qualities=outputs,
                    trailer_file=trailer_path,
                    trailer_status=trailer_status
                ),
                loop
            )
            logger.info(f"Database updated successfully for video {video_id}")
        except Exception as db_error:
            logger.error(f"Database update failed: {db_error}", exc_info=True)
            raise
        
        if failed:
            logger.warning(f"Video {video_id} converted with failures: {failed}")
        else:
            logger.info(f"Video {video_id} fully converted: {outputs}")
            
    except Exception as e:
        logger.error(f"Conversion failed for video {video_id}: {e}", exc_info=True)
        try:
            run_async_from_thread(
                update_video_status(video_id=video_id, status="failed", trailer_status="failed"),
                loop
            )
        except Exception as db_error:
            logger.error(f"Failed to update status to 'failed': {db_error}")

async def handle_video_conversion(
    input_path: str,
    title: str,
    description: str,
    duration: int,
    genre_id: int,
    generate_trailer: bool
) -> dict:
    genre = await Genre.get_or_none(uuid=genre_id)
    if not genre:
        raise Exception(f"Genre with ID {genre_id} not found")
    
    video = await Video.create(
        title=title,
        description=description,
        duration=duration,
        genre=genre,
        status="processing",
        file_path=input_path,
        output_file=None,
        qualities=None,
        trailer_file=None,
        trailer_status="none"
    )
    
    safe_title = sanitize_filename(title)
    output_filename = f"{video.id}_{safe_title}.mp4"
    output_path = os.path.join(CONVERTED_DIR, output_filename)
    
    loop = asyncio.get_running_loop()
    executor.submit(convert_and_update, video.id, input_path, output_path, generate_trailer, loop)
    
    return {
        "video_id": video.id,
        "status": "processing",
        "message": "Conversion started in background"
    }