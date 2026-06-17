from aiogram.types import Message
from aiogram.filters import CommandObject


async def start(message: Message) -> None:
    """Avvia il bot"""
    await message.reply('Bot ancora in beta! Ritorna più tardi :)')


async def help(message: Message) -> None:
    """Mostra la lista dei comandi"""

    await message.reply("""Ecco una lista dei comandi:
    /start - Avvia il bot
    /help - Mostra questo menù
    /echo - Ripete la parola data
    /deid - Restituisce il gioco della Wii o Gamecube corrispondente all'ID dato.
    /id   - Restituisce l'ID di un gioco della Wii o Gamecube dato il nome.""")


async def echo(message: Message, command: CommandObject) -> None:
    """Ripete la frase data come argomento."""

    await message.reply(
        command.args
        if command.args
        else "Scrivi qualcosa dopo /echo! Es: /echo ciao a tutti"
    )


async def deid(message: Message, command: CommandObject) -> None:
    """Data la lista di ID di giochi WII / GC, trova i nomi dei giochi corrispondenti."""
    
    if not command.args:
        await message.reply("Scrivere l'ID dei giochi da cercare dopo lo /. \nesempio: /deid R8PE01 ST7P01")
        return


    from utils.get_titles_by_ids import get_titles_by_ids

    game_names: list[str] = get_titles_by_ids(command.args.split())

    response = "\n".join(game_names)
    await message.reply(response)


async def id(message: Message, command: CommandObject) -> None:
    """Dato il nome di un gioco, restituisce l'ID del gioco corrispondente"""

    #TODO: Dare la possibilità di cercare la regione del gioco (pal, ntsc-u, ntsc-j). Per ora il predefinito è PAL. 

    if not command.args:
        await message.reply("Inserire il del gioco dopo lo /. \nEsempio: /id Super Smash. Bros Brawl")
        return
    
    
    # if len(command.args) < 2:
    #     await message.reply("Inserire regione e nome del gioco dopo lo /. \nEsempio: /id PAL Super Smash. Bros Brawl")

    #region = command.args[0]
    title = command.args

    from utils.get_ids_by_title import get_ids_by_title

    ids = get_ids_by_title(title, "PAL", 0.9)
    
    if ids == []:
        response = "Gioco non trovato"
    else:
        response = ids[0]

    await message.reply(response)


async def copertina_id(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.reply("Inserisci un ID!")
        return

    args = command.args.split()
    lang_codes=["EN", "JA", "FR", "DE", "ES", "IT", "NL", "PT", "RU", "KO", "ZHCN", "ZHTW"]
    id = args[0]
    lang_code = "EN"  if id[3] != 'J' else "JA"
    if len(args) > 1: 
        lang_code = args[1].upper()
        if lang_code not in lang_codes:
            await message.reply("Codice della lingua non valido.")
            return

    try:
        await message.reply_photo(f"https://art.gametdb.com/wii/coverfullHQ/{lang_code}/{id}.png")
    except:
        await message.reply("Apparentemente non esiste una copertina di questo gioco su GameTDB nella lingua specificata..")
        

async def info(message: Message, command: CommandObject) -> None:
    if not command.args \
    or len(args := command.args.split()) != 2 \
    or len(lang := args[0].upper()) not in {2, 4} \
    or len(title_id := args[1].upper()) not in {4, 6}:
        await message.reply("Inserisci la lingua e l'ID del titolo. Es: IT ST7P01\nNota: i WiiWare non hanno bisogno delle due lettere finali")
        return

    from utils.get_title_page import get_title_page
    import traceback
    
    reply: Message = await message.reply("Generando le informazioni...")
    try:
        await reply.edit_text(rich_message= await get_title_page(lang, title_id))
    except Exception:
        print(traceback.format_exc())
        await reply.edit_text("Titolo non trovato o errore nella generazione della pagina.")