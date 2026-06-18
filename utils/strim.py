import re


def strim(text: str) -> str:
    return re.sub(
        pattern= r"\s+", 
        repl= ' ',
        string= text.strip()
    )