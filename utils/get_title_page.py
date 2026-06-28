from .database import get_cursor
from aiogram.types.input_rich_message import InputRichMessage
from async_lru import alru_cache
from utils.fetch_url_head import fetch_cover_head

LANG_FLAGS: dict[str, str] = {
    'JA': '🇯🇵',
    'EN': '🇬🇧',
    'US': '🇺🇸',
    'DE': '🇩🇪',
    'FR': '🇫🇷',
    'FR': '🇫🇷',
    'IT': '🇮🇹',
    'ES': '🇪🇸',
    'KO': '🇰🇷',
    'SE': '🇸🇪',
    'FI': '🇫🇮',
    'NL': '🇳🇱',
    'DK': '🇩🇰',
    'PT': '🇵🇹',
    'NO': '🇳🇴',
    'RU': '🇷🇺',
    'TR': '🇹🇷',
    'ZHCN': '🇨🇳',
    'ZHTW': '🇹🇼'
}


@alru_cache()
async def get_title_page(
    lang: str = 'IT',
    title_console: str = 'Wii',
    title_id: str = 'ST7P01',
    morphable_lang: bool = True,
) -> InputRichMessage:
    is_full_title_id: bool = len(title_id) == 6
    title_artworks: list[str] = []
    title_other_titleIDs: list[str] = []
    title_other_names: dict[str, str] = {}

    cursor = get_cursor()
    # Aggiungi fallback alle lingue per titolo e sinossi,
    # cambiando il valore del parametro lang e title_region
    for lang in (lang, 'US', 'EN', 'JA'):
        if results := cursor.execute(
            f"""SELECT Title, Synopsis, MiniID, Region, MiniID || Region || COALESCE(PublisherID, '')
            FROM GameLocalePublisher
            WHERE Lang = ? AND MiniID = ? AND Console = ? {'AND Region = ?' if morphable_lang else ''}
            AND PublisherID IS{' NOT' if is_full_title_id else ''} NULL""",
            [lang, title_id[:3], title_console, title_id[3]]
            if morphable_lang else
            [lang, title_id[:3], title_console]
        ).fetchone():
            title_title, title_synopsis, title_mini_id, title_region, title_id = results
            english_japanese: bool = morphable_lang and lang == 'EN' and title_region == 'J'
            break
    else:
        raise
    
    # Ottieni altre informazioni essenziali sul titolo
    if results := cursor.execute(
        f"""SELECT g.Type, g.Developer, {'c.Name' if is_full_title_id else 'p.Publisher'}, r.Date, UNIXEPOCH(r.Date)
        FROM Game g
        JOIN GamePublisher p
        ON g.MiniID = p.MiniID AND g.Type = p.Type
        JOIN GameRelease r
        ON g.MiniID = r.MiniID AND g.Type = r.Type and r.Region = p.Region
        {'LEFT JOIN Company c ON p.PublisherID = c.Code AND p.Console = c.Console' if is_full_title_id else ''}
        WHERE g.MiniID = ? AND p.Region = ? 
        AND p.PublisherID IS{' NOT' if is_full_title_id else ''} NULL
        AND p.Console = ?
        LIMIT 1""",
        [title_mini_id, title_region, title_console]
    ).fetchone():
        title_type, title_developer, title_publisher, title_release_date, title_release_unix = results
    else:
        raise

    # Ottieni le informazioni per le altre lingue, insieme alle copertine
    japanese_transliteration: str = ""
    if results := cursor.execute(
        """SELECT DISTINCT Lang, Region, Title, LOWER(Console), MiniID || Region || COALESCE(PublisherID, '')
        FROM GameLocalePublisher
        WHERE MiniID = ? AND Type = ? AND Console = ?
        AND (Lang != 'JA' OR Region IN ('A', 'J'))
        AND (Lang != 'US' OR Region IN ('A', 'E', 'N', 'X', 'Y', 'Z'))
        AND (Lang != 'EN' OR Region IN ('A', 'P', 'H', 'U', 'X', 'Y', 'Z', 'J'))
        AND (Lang != 'DE' OR Region IN ('A', 'D', 'P', 'L', 'M', 'H', 'U', 'X', 'Y', 'Z'))
        AND (Lang != 'FR' OR Region IN ('A', 'F', 'P', 'L', 'M', 'H', 'U', 'X', 'Y', 'Z'))
        AND (Lang != 'IT' OR Region IN ('A', 'I', 'P', 'L', 'M', 'H', 'U', 'X', 'Y', 'Z'))
        AND (Lang != 'ES' OR Region IN ('A', 'S', 'P', 'L', 'M', 'H', 'U', 'X', 'Y', 'Z'))
        AND (Lang != 'KO' OR Region IN ('A', 'K', 'Q', 'T'))
        AND ((Lang != 'SE' AND Lang != 'FI') OR Region IN ('V', 'W'))
        AND ((Lang != 'ZHCN' AND Lang != 'ZHTW') OR Region = 'W')
        ORDER BY Region DESC""",
        [title_mini_id, title_type, title_console]
    ).fetchall():
        # Metti la copertina della lingua del gioco cercato come prima opzione, se presente
        if result_userlang := next((x for x in results if x[0] == ("JA" if english_japanese else lang)), None):
            results.insert(0, results.pop(results.index(result_userlang)))

        for result_lang, result_region, result_title, result_console, result_titleID in results:
            if result_titleID != title_id and result_titleID not in title_other_titleIDs:
                title_other_titleIDs.append(result_titleID)

            if result_lang == 'EN' and result_region == 'J':
                japanese_transliteration = result_title
            elif result_lang != lang:
                title_other_names[result_lang] = result_title

            # Controlla che tutte le copertine esistano, controllando l'head dell'url
            #* Il controllo degli URL è la parte più lenta di questa funzione!
            title_artworks.extend([
                f"![](https://art.gametdb.com/{result_console}/{atype[0]}/{result_lang}/{result_titleID}.{atype[1]})"
                for atype in {('coverfullHQ', 'png'), ('coverHQ', 'jpg')}
                if await fetch_cover_head(result_console, f"{result_lang}/{result_titleID}", atype)
            ])

    markdown: str = (
        f"{
            f'<tg-slideshow>{''.join(title_artworks)}</tg-slideshow>\n'
            if title_artworks else ''
        }"
        
        f"# {'🇯🇵🇬🇧' if english_japanese else LANG_FLAGS.get(lang, '❔')} {title_title}{'[^EN]' if lang == 'JA' else ''}\n"
        f"<sup>=={title_id}=={f", {', '.join(sorted(title_other_titleIDs))}" if title_other_titleIDs else ''}</sup>\n\n"

        f"{
            f'**Developer**: {title_developer}  \n'
            if title_developer else ''
        }"
        f"**Publisher**: {title_publisher}"
        f"{
            f'  \n**Released**: ![{title_release_date}](tg://time?unix={title_release_unix}&format=D)\n\n'
            if title_release_unix else "\n\n"
        }"

        f"{
            f'[^EN]: {japanese_transliteration}\n'
            if japanese_transliteration else ''
        }"

        f"{
            f'<details><summary>Synopsis</summary>\n> {title_synopsis.replace('\n', '\n> ')}</details>\n'
            if title_synopsis else ''
        }"

        f"{
            '<details><summary>ROM versions</summary>\n'
            '|Version|CRC|MD5|SHA1|\n'
            '|:-:|-|-|-|\n'
            f'{'\n'.join(
                f"| `{result_version}` | `{result_crc or '—'}` | `{result_md5 or '—'}` | `{result_sha1 or '—'}` |"
                for result_version, result_crc, result_md5, result_sha1 in results
            )}\n</details>\n'
            if (results := cursor.execute(
                """SELECT Version, CRC, MD5, SHA1
                FROM GameROM
                WHERE MiniID = ? AND Type = ? AND Region = ?""",
                [title_mini_id, title_type, title_region]
            ).fetchall()) else ''
        }"

        f"{
            f'<details><summary>Name in other languages</summary>\n{'  \n'.join(
                f"{LANG_FLAGS.get(result_lang, '❔')} **{result_title}**{'[^EN]' if result_lang == 'JA' and not english_japanese else ''}"
                for result_lang, result_title in title_other_names.items()
            )}</details>\n'
            if title_other_names else ''
        }"
    )

    cursor.close()
    return InputRichMessage(
        markdown=markdown,
        skip_entity_detection=True
    )
    

async def append_artworks(
    links_to_check: list[tuple[str, str, tuple[str, str]]],
    previous_rich: InputRichMessage,
) -> InputRichMessage:
    return InputRichMessage(
        markdown=(
            f"<tg-slideshow>{''.join([
                f"![](https://art.gametdb.com/{console}/{atype[0]}/{resource}.{atype[1]})"
                for console, resource, atype in links_to_check
                if await fetch_cover_head(console, resource, atype)
            ])}</tg-slideshow>\n"
            f"{previous_rich.markdown}"
        ),
        skip_entity_detection=True
    )