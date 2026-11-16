"""Тесты спецификации команд УВМ."""

from uvm.spec import COMMANDS, OPCODE, Field

ADDRESS_LIMIT = 65535
CONSTANT_LIMIT = 4194303
OPCODE_LIMIT = 31


def test_field_limit() -> None:
    """В поле из 16 бит помещаются числа до 65535."""
    assert Field("B", 5, 20).limit() == ADDRESS_LIMIT


def test_constant_field() -> None:
    """Константа занимает биты 21—42, то есть 22 бита."""
    assert COMMANDS["const"].fields[1].limit() == CONSTANT_LIMIT


def test_opcode_field() -> None:
    """Код операции — биты 0—4."""
    assert OPCODE.limit() == OPCODE_LIMIT


def test_opcodes() -> None:
    """Коды операций из спецификации."""
    opcodes = {name: command.opcode for name, command in COMMANDS.items()}
    assert opcodes == {"const": 0, "read": 26, "write": 10, "div": 4}


def test_fields_do_not_overlap() -> None:
    """Каждое поле начинается сразу после предыдущего."""
    for command in COMMANDS.values():
        previous = OPCODE
        for field in command.fields:
            assert field.first == previous.last + 1
            previous = field
