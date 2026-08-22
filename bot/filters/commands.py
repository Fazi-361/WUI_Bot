from aiogram.filters import Command
from aiogram.filters.command import CommandPatternType
from aiogram.types import BotCommand

start_botcommand = BotCommand(command="start", description="")
help_botcommand = BotCommand(command="help", description="")
settings_botcommand = BotCommand(command="settings", description="")
info_botcommand = BotCommand(command="info", description="")
id_botcommand = BotCommand(command="id", description="")


# Classe Command personalizzata per impostare i prefissi
# e le impostazioni di base per ogni comando predefinito
class CCommand(Command):
    prefix: str = "/!.,;?"

    def __init__(
        self,
        *values: CommandPatternType,
        commands: tuple[CommandPatternType, ...] | CommandPatternType | None = None
    ) -> None:
        super().__init__(
            *values,
            commands=commands,
            prefix=self.prefix,
            ignore_case=True,
            ignore_mention=False,
        )
