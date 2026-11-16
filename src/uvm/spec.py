"""Спецификация команд учебной виртуальной машины (УВМ)."""

from dataclasses import dataclass

COMMAND_SIZE = 7


class UvmError(Exception):
    """Ошибка в программе для УВМ."""


@dataclass(frozen=True)
class Field:
    """Поле команды: имя, номер первого и последнего бита."""

    name: str
    first: int
    last: int

    def limit(self) -> int:
        """Возвращает наибольшее число, которое помещается в поле."""
        return (1 << (self.last - self.first + 1)) - 1


@dataclass(frozen=True)
class Command:
    """Команда УВМ: код операции (поле A) и поля операндов."""

    opcode: int
    fields: tuple[Field, ...]


OPCODE = Field("A", 0, 4)

COMMANDS = {
    "const": Command(0, (Field("B", 5, 20), Field("C", 21, 42))),
    "read": Command(26, (Field("B", 5, 20), Field("C", 21, 36))),
    "write": Command(10, (Field("B", 5, 20), Field("C", 21, 36))),
    "div": Command(
        4, (Field("B", 5, 20), Field("C", 21, 36), Field("D", 37, 52))
    ),
}
