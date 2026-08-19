from . import get_cursor


def title_exists(title_id: str) -> bool:
    """
    Controlla se un titolo Wii esiste nel database dall'ID
    """

    if len(title_id) not in {4, 6}:
        return False
    
    title_id = title_id.upper()
    publisher: str = title_id[4:6]
    cursor = get_cursor()
    
    result = cursor.execute(
        f"""SELECT 1
        FROM GamePublisher
        WHERE Console = 'Wii'
        AND MiniID = ?
        AND Region = ?
        {"AND PublisherID = ?" if publisher else ''}
        """,
        [title_id[:3], title_id[3]]
        + ([publisher] if publisher else [])
    ).fetchone()

    cursor.close()
    return bool(result)