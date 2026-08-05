from .database import get_cursor
from aiogram.types.input_rich_message import InputRichMessage
from async_lru import alru_cache
from utils.fetch_url_head import filter_covers

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
    title_console: str = 'Wii',
    title_type: str | None = None,
    title_id: str = 'ST7P01',
    lang: str = 'IT',
    morphable_lang: bool = True,
) -> InputRichMessage:
    if not title_type:
        title_type = 'Wii' if len(title_id) == 6 else "Channel"

    title_mini_id: str = title_id[:3]
    title_artworks: list[str] = []
    title_other_titleIDs: list[str] = []
    title_other_names: dict[str, str] = {}

    cursor = get_cursor()
    # Aggiungi fallback alle lingue per titolo e sinossi,
    # cambiando il valore del parametro lang e title_region
    for lang in (lang, 'US', 'EN', 'JA'):
        if results := cursor.execute(
            f"""SELECT 
                Title,
                Synopsis,
                Region,
                MiniID || Region || COALESCE(PublisherID, ''),
                Developer,
                PublishDate,
                UNIXEPOCH(PublishDate),
                PublisherID,
                PublisherName
            FROM BaseGameLocale
            WHERE Console = ?
            AND GameType = ?
            AND MiniID = ?
            AND Lang = ?
            {'AND Region = ?' if morphable_lang else ''}
            LIMIT 1""",
            [title_console, title_type, title_mini_id, lang, title_id[3]]
            if morphable_lang else
            [title_console, title_type, title_mini_id, lang]
        ).fetchone():
            title_title, title_synopsis, title_region, title_id, \
                title_developer, title_release_date, title_release_unix, \
                title_publisher_id, title_publisher = results

            if not title_publisher \
            and (results := cursor.execute(
                """SELECT CompanyName
                FROM Company
                WHERE Console = ?
                AND CompanyCode = ?
                LIMIT 1""",
                [title_console, title_publisher_id]
            ).fetchone()):
                title_publisher = results[0]
            
            english_japanese: bool = morphable_lang and lang == 'EN' and title_region == 'J'
            break
    else:
        raise

    # Ottieni le informazioni per le altre lingue, insieme alle copertine
    japanese_transliteration: str = ""
    if results := cursor.execute(
        """SELECT DISTINCT Lang, Region, Title, LOWER(Console), MiniID || Region || COALESCE(PublisherID, '')
        FROM BaseGameLocale
        WHERE Console = ? AND GameType = ? AND MiniID = ?
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
        [title_console, title_type, title_mini_id]
    ).fetchall():
        for result_lang, result_region, result_title, result_console, result_titleID in results:
            if result_titleID != title_id and result_titleID not in title_other_titleIDs:
                title_other_titleIDs.append(result_titleID)

            if result_lang == 'EN' and result_region == 'J':
                japanese_transliteration = result_title
            elif result_lang != lang:
                title_other_names[result_lang] = result_title

            title_artworks.extend(
                f"{result_console}/{atype[0]}/{result_lang}/{result_titleID}.{atype[1]}"
                for atype in {('coverfullHQ', 'png'), ('coverHQ', 'jpg')}
            )
        else:
            # Controlla che tutte le copertine esistano, controllando l'head degli url
            #* Il controllo degli URL è la parte più lenta di questa funzione!
            title_artworks = [
                f"![](https://art.gametdb.com/{resource})"
                for resource in
                await filter_covers(frozenset(title_artworks))
            ]

            # Sposta la copertina della lingua del gioco cercato come prima opzione
            for filter_lang in ("JA" if english_japanese else lang, 'US', 'EN', 'JA'):
                if artwork_userlang := next(
                    (_ for _ in title_artworks if _[(i := _.rfind('/')) - 2:i] == filter_lang),
                    None
                ):
                    title_artworks.remove(artwork_userlang)
                    title_artworks.insert(0, artwork_userlang)
                    break

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
        f"{
            f'**Publisher**: {title_publisher}  \n'
            if title_publisher else ''
        }"
        f"{
            f'**Released**: ![{title_release_date}](tg://time?unix={title_release_unix}&format=D)\n\n'
            if title_release_unix else "\n\n"
        }"

        f"{
            f'<details><summary>Synopsis</summary>\n> {title_synopsis.replace('\n', '\n> ')}</details>\n'
            if title_synopsis else ''
        }"

        f"{
            '<details><summary>ROM versions</summary>\n'
            'Version|CRC|MD5|SHA1\n'
            '::|-|-|-\n'
            f'{'\n'.join(
                f"`{result_version}`|`{result_crc or '—'}`|`{result_md5 or '—'}`|`{result_sha1 or '—'}`"
                for result_version, result_crc, result_md5, result_sha1 in results
            )}\n</details>\n'
            if (results := cursor.execute(
                """SELECT ROMVersion, CRC, MD5, SHA1
                FROM GameROM
                WHERE GameType = ? AND MiniID = ? AND Region = ?""",
                [title_type, title_mini_id, title_region]
            ).fetchall()) else ''
        }"

        f"{
            f'<details><summary>Name in other languages</summary>\n{'  \n'.join(
                f"{LANG_FLAGS.get(result_lang, '❔')} **{result_title}**{'[^EN]' if result_lang == 'JA' and not english_japanese else ''}"
                for result_lang, result_title in title_other_names.items()
            )}</details>\n'
            if title_other_names else ''
        }"
        
        f"{
            f'[^EN]: {japanese_transliteration}\n'
            if japanese_transliteration else ''
        }"
    )

    cursor.close()
    return InputRichMessage(
        markdown=markdown,
        skip_entity_detection=True
    )
