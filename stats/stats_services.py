import datetime
import logging

from common.models import Stat, Video


async def update_stats(data: dict):
    try:
        video_uuid = data.get("video_uuid")
        stat_type = data.get("type")

        if not video_uuid or stat_type not in {"add_bookmark","remove_bookmark","as_view","stop","pause","play"}:
            logging.warning(f"Message invalide: {data}")
            return

        stat = await Stat.get_or_none(video_id=video_uuid)
        if not stat:
            video = await Video.get_or_none(id=video_uuid)
            if not video:
                logging.warning(f"Vidéo introuvable: {video_uuid}")
                return
            stat = await Stat.create(video=video)
        setattr(stat, stat_type, getattr(stat, stat_type) + 1)
        await stat.save()
        with open("stats.log", "a") as f:
            f.write(f"{datetime.datetime.now()}: {data}\n")

    except Exception as e:
        logging.exception(f"Erreur lors de la mise à jour des stats: {e}")
