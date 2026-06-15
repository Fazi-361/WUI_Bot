import sqlite3, requests_async
from aiogram.types.input_rich_message import InputRichMessage


async def get_title_page(
    lang: str = 'IT',
    titleID: str = 'ST7P01'
) -> InputRichMessage:
    title_mini_id: str = titleID[:3]
    title_region: str = titleID[3]
    title_titleIDs: list[str] = [titleID]
    markdown: str = ""
    
    with sqlite3.connect("./data/database.db") as conn:
        results = conn.execute(
            """SELECT DISTINCT l.Type, l.Lang, l.MiniID, l.Region, p.PublisherID
            FROM (
                SELECT DISTINCT Lang, MiniID, Type, Region
                FROM GameLocale
                WHERE MiniID = ?
                AND LENGTH(LANG) = 2
                AND (LANG != 'EN' OR Region = 'P' OR Region = 'E')
                AND (LANG != 'ES' OR Region = 'P')
                AND LANG != 'KO'
                AND LANG != 'DK'
            ) l
            LEFT JOIN GamePublisher p
            ON l.MiniID = p.MiniID AND l.Type = p.Type AND l.Region = p.Region
            ORDER BY l.Region DESC""",
            [title_mini_id]
        ).fetchall()
        
        if results:
            markdown += "<tg-slideshow>\n"
            if result_userlang := next((x for x in results if x[1] == lang), None):
                results.insert(0, results.pop(results.index(result_userlang)))
        for result_type, result_lang, result_miniID, \
        result_region, result_publisherID in results:
            result_type = result_type.casefold()
            if result_type == "wiiware":
                result_type = "wii"

            result_titleID = f"{result_miniID}{result_region}{result_publisherID or ''}"
            if not result_titleID in title_titleIDs:
                title_titleIDs.append(result_titleID)
            
            cover_url = f"https://art.gametdb.com/{result_type}/coverfullHQ/{result_lang}/{result_titleID}.png"
            try:
                if not (await requests_async.head(cover_url, timeout=3)).status_code == 200:
                    continue
            except: continue
            
            markdown += f"![]({cover_url})"
        else:
            markdown += "</tg-slideshow>\n\n"
    
        result_title, result_synopsis = conn.execute(
            "SELECT Title, Synopsis FROM GameLocale WHERE LANG = ? AND Region = ? AND MiniID = ?",
            [lang, title_region, title_mini_id]
        ).fetchone()
        
        markdown += f"# {result_title}\n"
        markdown += f"<sup>{', '.join(f"[{f"=={x}==" if x == title_titleIDs[0] else x}](https://wiki.dolphin-emu.org/index.php?title={x})" for x in title_titleIDs)}</sup>\n"
        if result_synopsis: markdown += f"<details><summary>Synopsis</summary>\n> {result_synopsis.replace('\n', '\n>')}</details>"
    
    # TODO: continue
    
    return InputRichMessage(
        markdown=markdown,
        skip_entity_detection=True
    )