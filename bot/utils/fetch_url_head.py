from aiohttp import ClientSession, TCPConnector
from async_lru import alru_cache
from asyncio import gather


async def fetch_cover_head(session: ClientSession, resource: str) -> str | None:
    async with session.head(resource) as response:
        return resource if response.ok else None


@alru_cache(maxsize=None)
async def filter_covers(resources: frozenset[str]) -> list[str]:
    """
    Controlla l'esistenza delle cover da gametdb.com, rimuovendo automaticamente
    gli URL non validi attraverso il controllo dell'head.
    
    USO: `filter_covers(frozenset(["wii/coverfullHQ/IT/RSBP01.png", ...]))`
    
    Nota: resources è un frozenset in quanto la cache non dovrebbe cambiare se
    l'ordine della lista in ingresso cambia.
    """
    
    async with ClientSession(
        base_url="https://art.gametdb.com/",
        connector=TCPConnector(ssl=False),
        conn_timeout=2
    ) as session:
        return [
            url for url in (await gather(*[
                fetch_cover_head(session, resource)
                for resource in resources
            ], return_exceptions=True))
            if isinstance(url, str)
        ]
