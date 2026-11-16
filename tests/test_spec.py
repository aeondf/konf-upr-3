"""Тесты спецификации команд УВМ."""

import pytest

from uvm.spec import (
    COMMAND_SIZE,
    COMMANDS,
    OPCODE,
    Field,
    UvmError,
    decode,
    encode,
)

ADDRESS_LIMIT = 65535
CONSTANT_LIMIT = 4194303
OPCODE_LIMIT = 31
LAST_BYTE_OF_D = 0x1F


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


@pytest.mark.parametrize(
    ("fields", "code"),
    [
        (
            {"A": 0, "B": 327, "C": 452},
            [0xE0, 0x28, 0x80, 0x38, 0x00, 0x00, 0x00],
        ),
        (
            {"A": 26, "B": 786, "C": 303},
            [0x5A, 0x62, 0xE0, 0x25, 0x00, 0x00, 0x00],
        ),
        (
            {"A": 10, "B": 124, "C": 13},
            [0x8A, 0x0F, 0xA0, 0x01, 0x00, 0x00, 0x00],
        ),
        (
            {"A": 4, "B": 371, "C": 880, "D": 359},
            [0x64, 0x2E, 0x00, 0x6E, 0xE0, 0x2C, 0x00],
        ),
    ],
)
def test_encode_spec_tests(fields: dict[str, int], code: list[int]) -> None:
    """Байты совпадают с тестами из спецификации."""
    assert encode(fields) == bytes(code)


def test_encode_max_values() -> None:
    """Наибольшие значения полей не вылезают за 7 байт."""
    code = encode({"A": 4, "B": 65535, "C": 65535, "D": 65535})
    assert len(code) == COMMAND_SIZE
    assert code[-1] == LAST_BYTE_OF_D


@pytest.mark.parametrize(
    "fields",
    [
        {"A": 0, "B": 327, "C": 452},
        {"A": 26, "B": 786, "C": 303},
        {"A": 10, "B": 124, "C": 13},
        {"A": 4, "B": 371, "C": 880, "D": 359},
        {"A": 0, "B": 65535, "C": 4194303},
    ],
)
def test_decode_is_reverse_of_encode(fields: dict[str, int]) -> None:
    """После перевода в байты и обратно получаются те же поля."""
    assert decode(encode(fields)) == fields


def test_decode_unknown_opcode() -> None:
    """Неизвестный код операции — ошибка."""
    with pytest.raises(UvmError, match="unknown command code A=1"):
        decode(bytes([1, 0, 0, 0, 0, 0, 0]))
