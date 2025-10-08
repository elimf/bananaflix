from urllib.parse import urlencode

async def search_key_builder(*args, **kwargs):

    request = kwargs.get("request")
    if not request:
        return "search_cache:no_request"

    params_str = urlencode(sorted(request.query_params.items())) or "no_params"

    return f"search_cache:{params_str}"