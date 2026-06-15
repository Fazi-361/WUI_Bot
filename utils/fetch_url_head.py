import requests_async
from async_lru import alru_cache


@alru_cache(maxsize=None)
async def fetch_url_head(url: str) -> bool:
    try: return (await requests_async.head(url, timeout=3)).status_code == 200
    except: return False