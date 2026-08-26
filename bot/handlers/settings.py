from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputRichMessage, Message
from aiogram.utils.i18n import FSMI18nMiddleware, I18n

from bot.filters import Administrator, CCommand, settings_botcommand

from ..filters.callbacks import SettingsCallback
from ..utils import S

settings_router: Router = Router()
settings_router.message.filter(CCommand(settings_botcommand), Administrator())
settings_router.callback_query.filter(SettingsCallback.filter())

LANGUAGE_BUTTON_ROWS: tuple[tuple[tuple[str, str, str], ...], ...] = (
    (
        ("US", SettingsCallback(option="US").pack(), "🇺🇸 US"),
        ("EN", SettingsCallback(option="EN").pack(), "🇬🇧 EN"),
        ("DE", SettingsCallback(option="DE").pack(), "🇩🇪 DE"),
        ("FR", SettingsCallback(option="FR").pack(), "🇫🇷 FR"),
    ),
    (
        ("ES", SettingsCallback(option="ES").pack(), "🇪🇸 ES"),
        ("IT", SettingsCallback(option="IT").pack(), "🇮🇹 IT"),
        ("JA", SettingsCallback(option="JA").pack(), "🇯🇵 JA"),
        ("KO", SettingsCallback(option="KO").pack(), "🇰🇷 KO"),
    ),
)
SHOW_COVERS: str = SettingsCallback(option=S.show_covers.name).pack()


@settings_router.message()
async def settings(message: Message, state: FSMContext, i18n: I18n) -> None:
    await message.reply_rich(get_settings_page(await state.get_data(), i18n))


@settings_router.callback_query(Administrator())
async def set_settings(
    query: CallbackQuery,
    callback_data: SettingsCallback,
    state: FSMContext,
    i18n_middleware: FSMI18nMiddleware,
    i18n: I18n,
) -> None:
    if data := query.data:
        _ = i18n.gettext
        option: str = callback_data.option

        if data == SHOW_COVERS:
            await state.update_data({option: not await state.get_value(option, S[option].value)})
        elif option in i18n.available_locales:
            await i18n_middleware.set_locale(state, option)
        else:
            await query.answer(_("settings.unknown"))
            return

        await query.answer(_("settings.saved"))
        await query.message.edit_text(rich_message=get_settings_page(await state.get_data(), i18n))  # type: ignore
        try: pass
        except:
            pass


@settings_router.callback_query()
async def no_admin(query: CallbackQuery, i18n: I18n) -> None:
    await query.answer(i18n.gettext("settings.no_admin"))


def get_settings_page(state_data: dict, i18n: I18n) -> InputRichMessage:
    _ = i18n.gettext
    true = lambda s: f"✅ {s}"
    false = lambda s: f"❌ {s}"
    locale: str = i18n.current_locale
    show_covers: bool = state_data.get(*S.show_covers.key)

    return InputRichMessage(
        markdown=f'**{_("settings.language")}**  \n'
        f'{''.join(f'<tg-button-row>{''.join(
            f'<tg-button {'style="primary" ' if locale == lang else ''}type="callback_data" data="{data}">{text}</tg-button>'
            for lang, data, text in row
        )}</tg-button-row>' for row in LANGUAGE_BUTTON_ROWS)}  \n'
        f'*{_("settings.language.description")}*'
        "\n\n---\n\n"
        f'**{_("settings.show_covers")}**: '
        f'<tg-button {'style="primary" ' if show_covers else ''}type="callback_data" data="{SHOW_COVERS}">{true(_('settings.on')) if show_covers else false(_('settings.off'))}</tg-button>  \n'
        f'*{_("settings.show_covers.description")}*',
        skip_entity_detection=True
    )
