import sqlite3
from aiogram.types.input_rich_message import InputRichMessage
from async_lru import alru_cache
from utils.fetch_url_head import fetch_url_head


@alru_cache()
async def get_title_page(
    lang: str = 'IT',
    title_id: str = 'ST7P01'
) -> InputRichMessage:
    title_id_len: int = len(title_id)
    is_full_title_id: bool = title_id_len == 6
    title_mini_id: str = title_id[:3]
    title_titleIDs: list[str] = [title_id]
    markdown: str = ""
    
    with sqlite3.connect("./data/database.db") as conn:
        results = conn.execute(
            """SELECT DISTINCT l.Lang, l.MiniID, l.Region, p.PublisherID
            FROM (
                SELECT DISTINCT Lang, MiniID, Type, Region
                FROM GameLocale
                WHERE MiniID = ?
                AND (Lang != 'JA' OR Region IN ('A', 'J'))
                AND ((Lang != 'EN' AND Lang != 'US') OR Region IN ('A', 'P', 'E', 'N'))
                AND (Lang != 'DE' OR Region IN ('A', 'D', 'P', 'L', 'M'))
                AND (Lang != 'FR' OR Region IN ('A', 'F', 'P', 'L', 'M'))
                AND (Lang != 'IT' OR Region IN ('A', 'I', 'P', 'L', 'M'))
                AND (Lang != 'ES' OR Region IN ('A', 'S', 'P', 'L', 'M'))
                AND (Lang != 'KO' OR Region IN ('A', 'K', 'Q', 'T'))
                AND ((Lang != 'SE' AND Lang != 'FI') OR Region IN ('V', 'W'))
                AND ((Lang != 'ZHCN' AND Lang != 'ZHTW') OR Region = 'W')
            ) l
            LEFT JOIN GamePublisher p
            ON l.MiniID = p.MiniID AND l.Type = p.Type AND l.Region = p.Region"""
            f" WHERE p.PublisherID IS{' NOT' if is_full_title_id else ''} NULL"
            " ORDER BY l.Region DESC",
            [title_mini_id]
        ).fetchall()
        
        if results:
            markdown += "<tg-slideshow>\n"
            # Metti la copertina della lingua del gioco cercato come prima opzione, se presente
            if result_userlang := next((x for x in results if x[0] == lang), None):
                results.insert(0, results.pop(results.index(result_userlang)))
        for result_lang, result_miniID, \
        result_region, result_publisherID in results:
            result_titleID = f"{result_miniID}{result_region}{result_publisherID or ''}"
            if not result_titleID in title_titleIDs:
                title_titleIDs.append(result_titleID)
            
            # Controlla che tutte le copertine esistano, controllando l'head dell'url
            cover_url = f"https://art.gametdb.com/wii/coverfullHQ/{result_lang}/{result_titleID}.png"
            if not await fetch_url_head(cover_url):
                continue
            
            markdown += f"![]({cover_url})"
        else:
            markdown += "</tg-slideshow>\n\n"
    
        # Aggiungi fallback alle lingue. Prova l'inglese come seconda opzione, poi il giapponese
        result_title, result_synopsis = None, None
        for test_lang in (lang, 'EN', 'US', 'JA'):
            try:
                result_title, result_synopsis = conn.execute(
                    """SELECT l.Title, l.Synopsis
                    FROM Game g
                    LEFT JOIN GameLocale l
                    ON l.MiniID = g.MiniID AND l.Type = g.Type
                    LEFT JOIN GamePublisher p
                    ON g.MiniID = p.MiniID AND g.Type = p.Type AND l.Region = p.Region
                    WHERE l.Lang = ? AND l.MiniID = ?"""
                    f" AND p.PublisherID IS {' NOT' if is_full_title_id else ''} NULL"
                    " ORDER BY l.Region DESC",
                    [test_lang, title_mini_id]
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