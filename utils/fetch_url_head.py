import requests_async
from async_lru import alru_cache


@alru_cache(maxsize=None)
async def fetch_url_head(url: str) -> bool:
    try: return (await requests_async.head(url, timeout=3)).status_code == 200
    except: return False
    

@alru_cache(maxsize=None)
async def fetch_cover_head(console: str, resource: str, atype: tuple[str, str] = ('coverfullHQ', 'png')) -> bool:
    try: return (await requests_async.head(f"https://art.gametdb.com/{console}/{atype[0]}/{resource}.{atype[1]}", timeout=2)).status_code == 200
    except: return False