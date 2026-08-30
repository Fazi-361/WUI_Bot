from functools import cache

from aiogram.types.input_rich_message import InputRichMessage
from aiogram.utils.i18n import get_i18n
from async_lru import alru_cache

from . import get_cursor, get_regions_by_title, get_title_roms
from ..utils.fetch_url_head import filter_covers

LANG_FLAGS: dict[str, str] = {
    "JA": "🇯🇵",
    "EN": "🇬🇧",
    "US": "🇺🇸",
    "DE": "🇩🇪",
    "FR": "🇫🇷",
    "FR": "🇫🇷",
    "IT": "🇮🇹",
    "ES": "🇪🇸",
    "KO": "🇰🇷",
    "SE": "🇸🇪",
    "FI": "🇫🇮",
    "NL": "🇳🇱",
    "DK": "🇩🇰",
    "PT": "🇵🇹",
    "NO": "🇳🇴",
    "RU": "🇷🇺",
    "TR": "🇹🇷",
    "ZHCN": "🇨🇳",
    "ZHTW": "🇹🇼",
}


@cache
def get_title_info(
    title_console: str,
    title_type: str,
    title_id: str,
    user_lang: str,
    enforce_title_lang: bool = True,
) -> tuple[frozenset[str], bool, InputRichMessage]:
    _ = get_i18n().gettext
    if not title_type:
        title_type = "Wii" if len(title_id) == 6 else "Channel"

    title_mini_id: str = title_id[:3]

    cursor = get_cursor()
    # Aggiungi fallback alle lingue per titolo e sinossi,
    # cambiando il valore del parametro lang e title_region
    for user_lang in (user_lang, "US", "EN", "JA", ""):
        if results := cursor.execute(
            f"""SELECT
                Lang,
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
            {'AND Lang = ?' if user_lang else ''}
            {'AND Region = ?' if enforce_title_lang else ''}
            ORDER BY REGION DESC
            LIMIT 1""",
            [title_console, title_type, title_mini_id]
            + ([user_lang] if user_lang else [])
            + ([title_id[3]] if enforce_title_lang else []),
        ).fetchone():
            (
                page_lang,
                title_title,
                title_synopsis,
                title_region,
                title_id,
                title_developer,
                title_release_date,
                title_release_unix,
                title_publisher_id,
                title_publisher,
            ) = results

            if not title_publisher and (
                results := cursor.execute(
                    """SELECT CompanyName
                    FROM Company
                    WHERE Console = ?
                    AND CompanyCode = ?
                    LIMIT 1""",
                    [title_console, title_publisher_id],
                ).fetchone()
            ):
                title_publisher = results[0]

            japanenglish: bool = (
                enforce_title_lang and page_lang == "EN" and title_region == "J"
            )
            break
    else:
        raise

    # Ottieni le informazioni per le altre lingue, insieme alle copertine
    title_artworks: list[str] = []
    title_other_titleIDs: list[str] = []
    title_other_names: dict[str, str] = {}
    title_console_lower: str = title_console.lower()
    japanese_transliteration: str = ""
    for (
        result_lang,
        result_region,
        result_title,
        result_titleID,
    ) in get_regions_by_title(title_console, title_type, title_mini_id):
        if result_titleID != title_id and result_titleID not in title_other_titleIDs:
            title_other_titleIDs.append(result_titleID)

        if result_lang == "EN" and result_region == "J":
            japanese_transliteration = result_title
        elif result_lang != page_lang:
            title_other_names[result_lang] = result_title

        title_artworks.extend(
            f"{title_console_lower}/{atype[0]}/{result_lang}/{result_titleID}.{atype[1]}"
            for atype in {("coverfullHQ", "png"), ("coverHQ", "jpg")}
        )

    markdown: str = (
        f"# {'🇯🇵🇬🇧' if japanenglish else LANG_FLAGS.get(page_lang, '❔')} {title_title}"
        f"{f' <sup>(EN: {japanese_transliteration})</sup>  \n' if japanese_transliteration and page_lang == 'JA' != user_lang else ''}  \n"
        f"<sup>=={title_id}=={f", {', '.join(sorted(title_other_titleIDs))}" if title_other_titleIDs else ''}</sup>\n\n"
        f"{
            f'**{_("info.developer")}**: {title_developer}  \n'
            if title_developer else ''
        }"
        f"{
            f'**{_("info.publisher")}**: {title_publisher}  \n'
            if title_publisher else ''
        }"
        f"{
            f'{LANG_FLAGS.get("JA" if japanenglish else user_lang, '❔')} **{_("info.release_date")}**: ![{title_release_date}](tg://time?unix={title_release_unix}&format=D)\n\n'
            if title_release_unix else ""
        }"
        f"{
            f'<details><summary>{_("info.synopsis")}</summary>\n> {title_synopsis.replace('\n', '\n> ')}</details>\n'
            if title_synopsis else ''
        }"
        f"{
            f'<details><summary>{_("info.revisions")}</summary>\n'
            f'{_("info.revision.version")}|CRC|MD5|SHA1\n'
            '::|-|-|-\n'
            f'{''.join(
                f"`{result_version}`|`{result_crc or '—'}`|`{result_md5 or '—'}`|`{result_sha1 or '—'}`\n"
                for result_version, result_crc, result_md5, result_sha1 in results
            )}</details>\n' if (results := get_title_roms(title_console, title_type, title_mini_id, title_region)) else ''
        }"
        f"{
            f'<details><summary>{_("info.name_in_other_languages")}</summary>\n{'  \n'.join(
                f"{LANG_FLAGS.get(result_lang, '❔')} **{result_title}**" 
                f"{f' <sup>(EN: {japanese_transliteration})</sup>' if japanese_transliteration and result_lang == 'JA' != user_lang else ''}"
                for result_lang, result_title in title_other_names.items()
            )}</details>' # \n\n
            if title_other_names else ''
        }"
    )

    cursor.close()
    return (
        frozenset(title_artworks),
        japanenglish,
        InputRichMessage(markdown=markdown, skip_entity_detection=True),
    )


@alru_cache
async def get_title_covers(
    resources: frozenset[str], user_lang: str | None = None, japanenglish: bool = False
) -> str:
    # Controlla che tutte le copertine esistano, controllando l'head degli url
    # * Il controllo degli URL è la parte più lenta di questa funzione!
    title_artworks = [
        f"![](https://art.gametdb.com/{resource})"
        for resource in await filter_covers(resources)
    ]

    # Sposta la copertina della lingua del gioco cercato come prima opzione
    for filter_lang in ("JA" if japanenglish else user_lang, "US", "EN", "JA"):
        if artwork_userlang := next(
            (
                _
                for _ in title_artworks
                if _[(i := _.rfind("/")) - 2 : i] == filter_lang
            ),
            None,
        ):
            title_artworks.remove(artwork_userlang)
            title_artworks.insert(0, artwork_userlang)
            break

    return (
        f"<tg-slideshow>{''.join(title_artworks)}</tg-slideshow>"
        if title_artworks
        else ""
    )


async def get_title_page(
    _,
    show_covers: bool,
    title_console: str = "Wii",
    title_type: str | None = None,
    title_id: str = "ST7P01",
    user_lang: str = "IT",
    enforce_title_lang: bool = True,
):
    cache_size: int = get_title_info.cache_info().currsize
    resources, japanenglish, message = get_title_info(
        title_console, title_type, title_id, user_lang, enforce_title_lang
    )

    if show_covers:
        # Se get_title_info non ha messo in cache, esisterà la cache anche di get_title_covers
        if get_title_info.cache_info().currsize > cache_size:
            yield InputRichMessage(
                markdown=f"{_("info.fetching_covers")}\n\n{message.markdown}"
            )

        if prependix := await get_title_covers(resources, user_lang, japanenglish):
            yield InputRichMessage(markdown=f"{prependix}\n\n{message.markdown}")
            return

    yield message
