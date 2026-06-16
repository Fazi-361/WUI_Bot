import sqlite3
from aiogram.types.input_rich_message import InputRichMessage
from async_lru import alru_cache
from utils.fetch_url_head import fetch_url_head

LANG_FLAGS: dict[tuple[str, str], str] = {
    ('JA', 'J'): '🇯🇵',
    ('EN', 'P'): '🇬🇧',
    ('US', 'E'): '🇺🇸',
    ('DE', 'D'): '🇩🇪',
    ('DE', 'P'): '🇩🇪',
    ('FR', 'F'): '🇫🇷',
    ('FR', 'P'): '🇫🇷',
    ('IT', 'I'): '🇮🇹',
    ('IT', 'P'): '🇮🇹',
    ('ES', 'S'): '🇪🇸',
    ('ES', 'P'): '🇪🇸',
    ('KO', 'K'): '🇰🇷',
    ('SE', 'V'): '🇸🇪',
    ('SE', 'W'): '🇸🇪',
    ('FI', 'V'): '🇫🇮',
    ('ZHCN', 'W'): '🇨🇳',
    ('ZHTW', 'W'): '🇹🇼'
}


@alru_cache()
async def get_title_page(
    lang: str = 'IT',
    title_id: str = 'ST7P01'
) -> InputRichMessage:
    title_id_len: int = len(title_id)
    is_full_title_id: bool = title_id_len == 6
    title_mini_id: str = title_id[:3]
    title_region: str = title_id[3]
    title_titleIDs: list[str] = [title_id]
    markdown: str = ""
    
    with sqlite3.connect("./data/database.db") as conn:
        if results := conn.execute(
            """SELECT DISTINCT Lang, MiniID || Region || COALESCE(PublisherID, '')
            FROM GameLocalePublisher
            WHERE MiniID = ?
            AND (Lang != 'JA' OR Region IN ('A', 'J'))
            AND ((Lang != 'EN' AND Lang != 'US') OR Region IN ('A', 'P', 'E', 'N'))
            AND (Lang != 'DE' OR Region IN ('A', 'D', 'P', 'L', 'M'))
            AND (Lang != 'FR' OR Region IN ('A', 'F', 'P', 'L', 'M'))
            AND (Lang != 'IT' OR Region IN ('A', 'I', 'P', 'L', 'M'))
            AND (Lang != 'ES' OR Region IN ('A', 'S', 'P', 'L', 'M'))
            AND (Lang != 'KO' OR Region IN ('A', 'K', 'Q', 'T'))
            AND ((Lang != 'SE' AND Lang != 'FI') OR Region IN ('V', 'W'))
            AND ((Lang != 'ZHCN' AND Lang != 'ZHTW') OR Region = 'W')"""
            f" AND PublisherID IS{' NOT' if is_full_title_id else ''} NULL"
            " ORDER BY Region DESC",
            [title_mini_id]
        ).fetchall():
            markdown += "<tg-slideshow>\n"
            # Metti la copertina della lingua del gioco cercato come prima opzione, se presente
            if result_userlang := next((x for x in results if x[0] == lang), None):
                results.insert(0, results.pop(results.index(result_userlang)))

            for result_lang, result_titleID in results:
                if not result_titleID in title_titleIDs:
                    title_titleIDs.append(result_titleID)
                
                # Controlla che tutte le copertine esistano, controllando l'head dell'url
                cover_url = f"https://art.gametdb.com/wii/coverfullHQ/{result_lang}/{result_titleID}.png"
                if not await fetch_url_head(cover_url):
                    continue
                
                markdown += f"![]({cover_url})"

            markdown += "</tg-slideshow>\n\n"
        
        # Aggiungi fallback alle lingue per titolo e sinossi
        for test_lang, test_region in ((lang, title_region), ('US', 'E'), ('EN', 'P'), ('JA', 'J')):
            try: result_title, result_synopsis = conn.execute(
                    """SELECT Title, Synopsis
                    FROM GameLocalePublisher
                    WHERE Lang = ? AND MiniID = ? AND Region = ?"""
                    f" AND PublisherID IS{' NOT' if is_full_title_id else ''} NULL",
                    [test_lang, title_mini_id, test_region]
                ).fetchone()
            except: continue
            else:
                markdown += f"# {result_title}{'[^EN]' if test_lang == 'JA' else ''}\n"
                markdown += f"<sup>[{', '.join(f'=={x}==' if x == title_id else x for x in title_titleIDs)}](https://wiki.dolphin-emu.org/index.php?title={title_id})</sup>\n"
                if result_synopsis: markdown += f"<details><summary>Synopsis</summary>\n> {result_synopsis.replace('\n', '\n>')}</details>\n"

                # Ottieni il nome in tutte le altre lingue
                if results := conn.execute(
                    """SELECT DISTINCT Lang, Region, Title
                    FROM GameLocalePublisher
                    WHERE MiniID = ? AND NOT (Lang = ? AND Region = ?)"""
                    f" AND PublisherID IS{' NOT' if is_full_title_id else ''} NULL"
                    " ORDER BY Region DESC",
                    [title_mini_id, test_lang, test_region]
                ).fetchall():
                    if japanese_transliteration := [
                        x[2] for x in results
                        if x[0] == 'EN' and x[1] == 'J'    
                    ]:
                        markdown += f"[^EN]: {japanese_transliteration[0]}\n"
                    
                    if results := [
                        x + (flag,) for x in results
                        if (flag := LANG_FLAGS.get((x[0], x[1])))
                    ]:
                        markdown += f"<details><summary>Name in other languages</summary>\n"
                        
                        for result_lang, _, result_title, result_flag in results:
                            markdown += f"{result_flag} **{result_title}**{'[^EN]' if result_lang == 'JA' else ''}\n\n"
                        
                        markdown += f"</details>\n\n"
                                
                break
    
    # TODO: continue
    
    return InputRichMessage(
        markdown=markdown,
        skip_entity_detection=True
    )