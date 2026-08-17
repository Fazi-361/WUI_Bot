from functools import lru_cache
import re


@lru_cache()
def strim(text: str) -> str:
    return re.sub(
        pattern= r"\s+", 
        repl= ' ',
        string= text.strip()
    )
