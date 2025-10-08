from common.models import Stat


async def request_key_builder(*args, **kwargs):
    latest_stats = (
        await Stat.all().order_by("-updated_at").values_list("updated_at", flat=True)
    )
    updated_at = latest_stats[0] if latest_stats else "none"

    return f"stats_cache_{updated_at}"

