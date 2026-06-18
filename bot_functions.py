import traceback, re, constants as C
from utils.fsm import BotState
from utils.strim import strim
from utils.database import get_id_by_title
from aiogram import Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from utils.get_title_page import get_title_page

LANGUAGE_OPTIONS = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇺🇸 US", callback_data='US'),
        InlineKeyboardButton(text="🇬🇧 EN", callback_data='EN'),
        InlineKeyboardButton(text="🇩🇪 DE", callback_data='DE'),
        InlineKeyboardButton(text="🇫🇷 FR", callback_data='FR'),
    ],   
    [
        InlineKeyboardButton(text="🇪🇸 ES", callback_data='ES'),
        InlineKeyboardButton(text="🇮🇹 IT", callback_data='IT'),
        InlineKeyboardButton(text="🇯🇵 JA", callback_data='JA'),
        InlineKeyboardButton(text="🇰🇷 KO", callback_data='KO'),
    ],   
])


async def start(message: Message, state: FSMContext) -> None:
    """Avvia il bot"""
    
    if not await state.get_value("lang"):
        await state.set_state(BotState.language)
        await message.reply(
            "🇺🇸 Hello, Welcome to the bot! Select a default language to continue.\n\n"
            "🇮🇹 Ciao, benvenuti al bot! Seleziona una lingua predefinita per continuare.",
            reply_markup=LANGUAGE_OPTIONS
        )
    else:
        # TODO: rispondi nella linagua dell'utente [per il futuro con i18n?]
        await message.reply("Ciao! :)\nSe vuoi le impostazioni sulla lingua, digita /lingua")
    

async def lingua(message: Message, state: FSMContext) -> None:
    await message.reply(
        "🇺🇸 Select a default language to continue.\n\n"
        "🇮🇹 Seleziona una lingua predefinita per continuare.",
        reply_markup=LANGUAGE_OPTIONS
    )


async def set_language(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.update_data({"lang": query.data})
    await query.answer("Lingua impostata!")
    try: await query.message.edit_text("Lingua impostata! :)") # type: ignore
    except: pass


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

    title = command.args

    from utils.get_ids_by_title import get_ids_by_title

    games = get_ids_by_title(title, "PAL", 0.9)
    
    if games == []:
        response = "Non è stato trovato nessun gioco con questo nome"
    elif max(game.similarity for game in games) > 0.99:
        response = max(games, key=lambda game: game.similarity).id
    else:
        possible_games = "\n".join(f"{game.title} - {game.id}" for game in games)
        response = f"ID possibili:\n{possible_games}"

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
        

async def info(message: Message, command: CommandObject, state: FSMContext) -> None:
    if not (args := command.args) or not (args := strim(args).upper()):
        await message.reply(
            "Inserisci l'ID del titolo o il suo nome. Es:\n"
            "<pre>/info ST7P01</pre>\n"
            "<pre>/info Super Mario Galaxy</pre>\n"
            "Nota: i WiiWare non hanno bisogno delle due lettere finali"
        )
        return
    
    title_id = args \
        if (morphable_lang := bool(re.match(r"^[0-9CDEFGHJLMNPQRSWX][0-9A-Z]{2}[ABDEFHIJKLMNPQRSTUVWXYZ](?:[0-9A-Z]{2})?$", args))) \
        else get_id_by_title(args, C.LANG_REGIONS.get(await state.get_value("lang") or 'IT') or 'P')

    reply: Message = await message.reply("Generando le informazioni...")
    try:
        await reply.edit_text(rich_message= await get_title_page((await state.get_value("lang")) or 'IT', title_id, morphable_lang))
    except Exception:
        print(traceback.format_exc())
        await reply.edit_text("Titolo non trovato o errore nella generazione della pagina.")