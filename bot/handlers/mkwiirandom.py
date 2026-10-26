from random import choice, randrange

from aiogram import Router
from aiogram.filters import CommandObject
from aiogram.types import Message
from aiogram.utils.i18n import I18n

from ..filters import CCommand, mkwiirandom_botcommand
from ..utils.text import strim

mkwiirandom_router = Router()

mkwii: I18n = I18n(path="locales", default_locale="US", domain="mkwii")
mk__ = mkwii.lazy_gettext

CHARACTERS_VEHICLES_SIZE = (
    (
        (
            mk__("Baby Mario"),
            mk__("Baby Peach"),
            mk__("Toad"),
            mk__("Koopa Troopa"),
            mk__("Baby Luigi"),
            mk__("Baby Daisy"),
            mk__("Toadette"),
            mk__("Dry Bones"),
            mk__("Mii S"),
        ),
        (
            mk__("Standard Kart S"),
            mk__("Booster Seat"),
            mk__("Mini Beast"),
            mk__("Cheep Charger"),
            mk__("Tiny Titan"),
            mk__("Blue Falcon"),
            mk__("Standard Bike S"),
            mk__("Bullet Bike"),
            mk__("Bit Bike"),
            mk__("Quacker"),
            mk__("Magikruiser"),
            mk__("Jet Bubble"),
        ),
    ),
    (
        (
            mk__("Mario"),
            mk__("Luigi"),
            mk__("Peach"),
            mk__("Yoshi"),
            mk__("Daisy"),
            mk__("Birdo"),
            mk__("Diddy Kong"),
            mk__("Bowser Jr."),
            mk__("Mii M"),
        ),
        (
            mk__("Standard Kart M"),
            mk__("Classic Dragster"),
            mk__("Wild Wing"),
            mk__("Super Blooper"),
            mk__("Daytripper"),
            mk__("Sprinter"),
            mk__("Standard Bike M"),
            mk__("Mach Bike"),
            mk__("Sugarscoot"),
            mk__("Zip Zip"),
            mk__("Sneakster"),
            mk__("Dolphin Dasher"),
        ),
    ),
    (
        (
            mk__("Wario"),
            mk__("Waluigi"),
            mk__("Donkey Kong"),
            mk__("Bowser"),
            mk__("King Boo"),
            mk__("Rosalina"),
            mk__("Funky Kong"),
            mk__("Dry Bowser"),
            mk__("Mii L"),
        ),
        (
            mk__("Standard Kart L"),
            mk__("Offroader"),
            mk__("Flame Flyer"),
            mk__("Piranha Prowler"),
            mk__("Jetsetter"),
            mk__("Honeycoupe"),
            mk__("Standard Bike L"),
            mk__("Flame Runner"),
            mk__("Wario Bike"),
            mk__("Shooting Star"),
            mk__("Spear"),
            mk__("Phantom"),
        ),
    ),
)


@mkwiirandom_router.message(CCommand(mkwiirandom_botcommand))
def generate_random(message: Message, command: CommandObject, i18n: I18n):
    _ = i18n.gettext
    try:
        if not (
            (args := command.args)
            and (args := strim(args))
            and 1 <= (args := int(args)) <= 12
        ):
            raise
    except:
        return message.reply(_("command.mkwiirandom.usage"))

    with mkwii.use_locale(i18n.current_locale):
        return message.reply(
            "\n\n".join(
                (
                    lambda size: f'{_("mkwiirandom.player").format(i)}\n{choice(size[0])} — {choice(size[1])}'
                )(choice(CHARACTERS_VEHICLES_SIZE))
                for i in range(1, args + 1)
            )
        )
