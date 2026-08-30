from bot.database import use_cursor


def get_title_roms(
    title_console: str, title_type: str, title_mini_id: str, title_region: str | None
) -> list[tuple[str, str, str, str]]:
    with use_cursor() as cursor:
        return cursor.execute(
            f"""SELECT ROMVersion, CRC, MD5, SHA1
            FROM GameROM
            WHERE Console = ?
            AND GameType = ?
            AND MiniID = ?
            {'AND Region = ?' if title_region else ''}""",
            [title_console, title_type, title_mini_id, title_region]
            if title_region else
            [title_console, title_type, title_mini_id],
        ).fetchall()
