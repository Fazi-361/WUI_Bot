import sqlite3
from aiogram.types.input_rich_message import InputRichMessage
from async_lru import alru_cache
from utils.fetch_url_head import fetch_url_head


@alru_cache()
async def get_title_page(
    lang: str = 'IT',
    title_id: str = 'ST7P01'
) -> InputRichMessage:
    title_mini_id: str = title_id[:3]
    title_region: str = title_id[3]
    title_publisher_id: str | None = title_id[4:] or None
    title_titleIDs: list[str] = [title_id]
    markdown: str = ""
    
    with sqlite3.connect("./data/database.db") as conn:
        results = conn.execute(
            """SELECT DISTINCT l.Type, l.Lang, l.MiniID, l.Region, p.PublisherID
            FROM (
                SELECT DISTINCT Lang, MiniID, Type, Region
                FROM GameLocale
                WHERE MiniID = ?
                AND (Lang != 'JA' OR Region IN ('A', 'J'))
                AND (Lang != 'EN' OR Region IN ('A', 'P', 'E', 'N'))
                AND (Lang != 'DE' OR Region IN ('A', 'D', 'P', 'L', 'M'))
                AND (Lang != 'FR' OR Region IN ('A', 'F', 'P', 'L', 'M'))
                AND (Lang != 'IT' OR Region IN ('A', 'I', 'P', 'L', 'M'))
                AND (Lang != 'ES' OR Region IN ('A', 'S', 'P', 'L', 'M'))
                AND (Lang != 'KO' OR Region IN ('A', 'K', 'Q', 'T'))
                AND ((Lang != 'SE' AND Lang != 'FI') OR Region IN ('V', 'W'))
                AND ((Lang != 'ZHCN' AND Lang != 'ZHTW') OR Region = 'W')
            ) l
            LEFT JOIN GamePublisher p
            ON l.MiniID = p.MiniID AND l.Type = p.Type AND l.Region = p.Region
            WHERE p.PublisherID IS ?
            ORDER BY l.Region DESC""",
            [title_mini_id, title_publisher_id]
        ).fetchall()
        
        if results:
            markdown += "<tg-slideshow>\n"
            # Metti la copertina della lingua del gioco cercato come prima opzione, se presente
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
            
            # Controlla che tutte le copertine esistano, controllando l'head dell'url
            cover_url = f"https://art.gametdb.com/{result_type}/coverfullHQ/{result_lang}/{result_titleID}.png"
            if not await fetch_url_head(cover_url):
                continue
            
            markdown += f"![]({cover_url})"
        else:
            markdown += "</tg-slideshow>\n\n"
    
        # Aggiungi fallback alle lingue. Prova l'inglese come seconda opzione, poi il giapponese
        result_title, result_synopsis = None, None
        for test_lang in (lang, 'EN', 'JA'):
            try:
                result_title, result_synopsis = conn.execute(
                    """SELECT l.Title, l.Synopsis
                    FROM GameLocale l
                    LEFT JOIN GamePublisher p
                    ON l.MiniID = p.MiniID AND l.Type = p.Type AND l.Region = p.Region
                    WHERE l.LANG = ? AND l.Region = ? AND l.MiniID = ? AND p.PublisherID IS ?""",
                    [test_lang, title_region, title_mini_id, title_publisher_id]
                ).fetchone()
            except: continue
            else: break
        
        markdown += f"# {result_title}\n"
        markdown += f"<sup>[{', '.join(f'=={x}==' if x == title_id else x for x in title_titleIDs)}](https://wiki.dolphin-emu.org/index.php?title={title_id})</sup>\n"
        if result_synopsis: markdown += f"<details><summary>Synopsis</summary>\n> {result_synopsis.replace('\n', '\n>')}</details>"
    
    # TODO: continue
    
    return InputRichMessage(
        markdown=markdown,
        skip_entity_detection=True
    )