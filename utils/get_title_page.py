from .database import get_cursor
# from timeit import default_timer as timer
from aiogram.types.input_rich_message import InputRichMessage
from async_lru import alru_cache
from utils.fetch_url_head import fetch_cover_head

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
    title_id: str = 'ST7P01',
    morphable_lang: bool = True,
) -> InputRichMessage:
    # timer_start: float = timer()
    title_id_len: int = len(title_id)
    is_full_title_id: bool = title_id_len == 6
    title_mini_id: str = title_id[:3]
    title_region: str = title_id[3]
    title_titleIDs: list[str] = [title_id]
    markdown: str = ""
    
    cursor = get_cursor()
    # Aggiungi fallback alle lingue per titolo e sinossi,
    # cambiando il valore del parametro lang e title_region
    for lang in (lang, 'US', 'EN', 'JA'):
        if results := cursor.execute(
            f"""SELECT Title, Synopsis
            FROM GameLocalePublisher
            WHERE Lang = ? AND MiniID = ? {'AND Region = ?' if morphable_lang else ''}
            AND PublisherID IS{' NOT' if is_full_title_id else ''} NULL""",
            [lang, title_mini_id] + ([title_region] if morphable_lang else [])
        ).fetchone():
            result_title, result_synopsis = results
            english_japanese = lang == 'EN' and title_region == 'J'
            break
    else:
        raise
    
    if results := cursor.execute(
        f"""SELECT g.Type, g.Developer, {'c.Name' if is_full_title_id else 'p.Publisher'}, r.Date, UNIXEPOCH(r.Date)
        FROM Game g
        JOIN GamePublisher p
        ON g.MiniID = p.MiniID AND g.Type = p.Type
        JOIN GameRelease r
        ON g.MiniID = r.MiniID AND g.Type = r.Type and r.Region = p.Region
        {'LEFT JOIN Company c ON p.PublisherID = c.Code' if is_full_title_id else ''}
        WHERE g.MiniID = ? and p.Region = ?
        AND p.PublisherID IS{' NOT' if is_full_title_id else ''} NULL
        LIMIT 1""",
        [title_mini_id, title_region]
    ).fetchone():
        title_type, title_developer, title_publisher, title_release_date, title_release_unix = results
    else:
        raise
    
    if results := cursor.execute(
        """SELECT DISTINCT Lang, MiniID || Region || COALESCE(PublisherID, '')
        FROM GameLocalePublisher
        WHERE MiniID = ? AND Type = ?
        AND (Lang != 'JA' OR Region IN ('A', 'J'))
        AND ((Lang != 'EN' AND Lang != 'US') OR Region IN ('A', 'P', 'E', 'N'))
        AND (Lang != 'DE' OR Region IN ('A', 'D', 'P', 'L', 'M'))
        AND (Lang != 'FR' OR Region IN ('A', 'F', 'P', 'L', 'M'))
        AND (Lang != 'IT' OR Region IN ('A', 'I', 'P', 'L', 'M'))
        AND (Lang != 'ES' OR Region IN ('A', 'S', 'P', 'L', 'M'))
        AND (Lang != 'KO' OR Region IN ('A', 'K', 'Q', 'T'))
        AND ((Lang != 'SE' AND Lang != 'FI') OR Region IN ('V', 'W'))
        AND ((Lang != 'ZHCN' AND Lang != 'ZHTW') OR Region = 'W')
        ORDER BY Region DESC""",
        [title_mini_id, title_type]
    ).fetchall():
        markdown += "<tg-slideshow>\n"

        # Metti la copertina della lingua del gioco cercato come prima opzione, se presente
        cover_lang: str = "JA" if english_japanese else lang
        if result_userlang := next((x for x in results if x[0] == cover_lang), None):
            results.insert(0, results.pop(results.index(result_userlang)))

        for result_lang, result_titleID in results:
            if not result_titleID in title_titleIDs:
                title_titleIDs.append(result_titleID)
            
            # Controlla che tutte le copertine esistano, controllando l'head dell'url
            if not await fetch_cover_head(resource := f"{result_lang}/{result_titleID}"):
                continue
            
            markdown += f"![](https://art.gametdb.com/wii/coverfullHQ/{resource}.png)"

        markdown += "</tg-slideshow>\n"
    
    markdown += (
        f"# {result_title}{'[^EN]' if lang == 'JA' else ''}\n"
        f"<sup>[{', '.join(f'=={x}==' if x == title_id else x for x in title_titleIDs)}](https://wiki.dolphin-emu.org/index.php?title={title_id})</sup>\n"
        "\n"
        f"**Developer**: {title_developer}  \n"
        f"**Publisher**: {title_publisher}  \n"
        f"**Released**: ![{title_release_date}](tg://time?unix={title_release_unix}&format=D)\n\n"
    )
    
    if result_synopsis:
        markdown += f"<details><summary>Synopsis</summary>\n> {result_synopsis.replace('\n', '\n> ')}</details>\n"

    if results := cursor.execute(
        """SELECT Version, CRC, MD5, SHA1
        FROM GameROM
        WHERE MiniID = ? AND Type = ? AND Region = ?""",
        [title_mini_id, title_type, title_region]
    ):
        markdown += (
            "<details><summary>ISO versions</summary>\n"
            "| Version | CRC | MD5 | SHA1 |\n"
            "| :-: | - | - | - |\n"
        )
        
        for result_version, result_crc, result_md5, result_sha1 in results:
            markdown += f"| `{result_version}` | `{result_crc or '—'}` | `{result_md5 or '—'}` | `{result_sha1 or '—'}` |" 
        
        markdown += "</details>\n"

    # Ottieni il nome in tutte le altre lingue
    if results := cursor.execute(
        """SELECT DISTINCT Lang, Region, Title
        FROM GameLocale
        WHERE MiniID = ? AND NOT (Lang = ? AND Region = ?)
        AND Type = ?
        ORDER BY Region DESC""",
        [title_mini_id, lang, title_region, title_type]
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
            markdown += "<details><summary>Name in other languages</summary>\n"
            
            for result_lang, _, result_title, result_flag in results:
                markdown += f"{result_flag} **{result_title}**{'[^EN]' if result_lang == 'JA' and not english_japanese else ''}\n\n"
            
            markdown += "</details>\n"
    
    # markdown += f"<sub>*generato in {timer() - timer_start:.3f} secondi*</sub>"
    
    cursor.close()
    return InputRichMessage(
        markdown=markdown,
        skip_entity_detection=True
    )