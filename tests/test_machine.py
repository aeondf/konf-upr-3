"""Тесты учебной виртуальной машины."""

import pytest

from uvm.assembler import parse_program
from uvm.machine import MEMORY_SIZE, Machine
from uvm.spec import COMMAND_SIZE, UvmError, encode

VALUE = 77
TWO_COMMANDS = 2
QUOTIENT = 14


def assemble(text: str) -> bytes:
    """Переводит текст программы в машинный код."""
    program = parse_program(text, "test.csv")
    return b"".join(encode(fields) for fields in program)


def run(text: str) -> Machine:
    """Выполняет программу и возвращает машину после работы."""
    machine = Machine(assemble(text))
    machine.run()
    return machine


def test_program_is_in_memory() -> None:
    """Команды лежат в той же памяти, что и данные, с адреса 0."""
    code = assemble("const,1000,5")
    machine = Machine(code)
    assert machine.memory[:COMMAND_SIZE] == list(code)
    assert len(machine.memory) == MEMORY_SIZE


def test_run_counts_commands() -> None:
    """run() возвращает число выполненных команд."""
    machine = Machine(assemble("const,1000,5\nconst,1001,6"))
    assert machine.run() == TWO_COMMANDS


def test_load_const() -> None:
    """const: память[B] = C."""
    machine = run(f"const,1000,{VALUE}")
    assert machine.memory[1000] == VALUE


def test_read() -> None:
    """read: память[C] = память[память[B]]."""
    machine = run(f"const,1000,1100\nconst,1100,{VALUE}\nread,1000,1200")
    assert machine.memory[1200] == VALUE


def test_write() -> None:
    """write: память[память[C]] = память[B]."""
    machine = run(f"const,1000,{VALUE}\nconst,1001,1200\nwrite,1000,1001")
    assert machine.memory[1200] == VALUE


def test_divide() -> None:
    """div: память[D] = память[память[B]] / память[C], целая часть."""
    machine = run(
        "const,1000,1100\nconst,1100,100\nconst,1101,7\ndiv,1000,1101,1200"
    )
    assert machine.memory[1200] == QUOTIENT


def test_divide_by_zero() -> None:
    """Деление на ноль — ошибка."""
    with pytest.raises(UvmError, match="division by zero: cell 1101 is 0"):
        run("const,1000,1100\nconst,1100,5\ndiv,1000,1101,1200")


def test_bad_program_size() -> None:
    """Размер программы должен делиться на 7."""
    with pytest.raises(UvmError, match="not a multiple of 7"):
        Machine(bytes(8))


def test_address_outside_memory() -> None:
    """Адрес из ячейки может оказаться за пределами памяти."""
    with pytest.raises(UvmError, match="address 70000 is outside memory"):
        run("const,1000,70000\nread,1000,1001")


def test_overwritten_command() -> None:
    """Если программа затёрла свою команду числом, это ошибка."""
    with pytest.raises(UvmError, match="does not hold a command"):
        run("const,7,1000\nconst,1000,5")
