from aiogram.filters import Command
from aiogram.filters.command import CommandPatternType
from ..utils import constants as C


# Classe Command personalizzata per impostare i prefissi
# e le impostazioni di base per ogni comando predefinito
class CustomCommand(Command):
    prefix: str = C.COMMAND_PREFIX

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