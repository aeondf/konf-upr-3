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

BY_OPCODE = {command.opcode: command for command in COMMANDS.values()}


def encode(fields: dict[str, int]) -> bytes:
    """Собирает команду из полей в 7 байт, младший байт первым."""
    command = BY_OPCODE[fields["A"]]
    value = fields["A"]
    for field in command.fields:
        value |= fields[field.name] << field.first
    return value.to_bytes(COMMAND_SIZE, "little")


def decode(code: bytes) -> dict[str, int]:
    """Разбирает 7 байт машинного кода обратно на поля."""
    value = int.from_bytes(code, "little")
    opcode = value & OPCODE.limit()
    command = BY_OPCODE.get(opcode)
    if command is None:
        raise UvmError(f"unknown command code A={opcode}")
    fields = {"A": opcode}
    for field in command.fields:
        fields[field.name] = (value >> field.first) & field.limit()
    return fields
