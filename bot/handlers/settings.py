from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import FSMI18nMiddleware, I18n

from bot.filters.command import CustomCommand
from bot.keyboards.inline import LANGUAGE_OPTIONS

from ..utils.fsm import BotState

settings_router: Router = Router()


@settings_router.message(CustomCommand("settings"))
async def settings(message: Message, state: FSMContext) -> None:
    await state.set_state(BotState.language)
    await message.reply(
        "🇺🇸 Select a language to continue.\n"
        "🇩🇪 Wählen Sie eine Sprache aus, um fortzufahren.\n"
        "🇫🇷 Sélectionnez une langue pour continuer.\n"
        "🇪🇸 Selecciona un idioma para continuar.\n"
        "🇮🇹 Seleziona una lingua per continuare.\n"
        "🇯🇵 続行するには、言語を選択してください。\n"
        "🇰🇷 계속하려면 언어를 선택하세요.",
        reply_markup=LANGUAGE_OPTIONS,
    )


@settings_router.callback_query(BotState.language)
async def set_language(
    query: CallbackQuery,
    state: FSMContext,
    i18n_middleware: FSMI18nMiddleware,
    i18n: I18n,
) -> None:
    if data := query.data:
        _ = i18n.gettext
        await state.set_state(None)
        await i18n_middleware.set_locale(state, data)
        await query.answer(_("language.set.answer"))
        try: await query.message.edit_text(_("language.set.message"))  # type: ignore
        except: pass
