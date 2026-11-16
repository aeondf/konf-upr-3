"""Тесты готовых программ из папки programs."""

from pathlib import Path

from uvm.assembler import read_program
from uvm.machine import Machine
from uvm.spec import encode

PROGRAMS = Path(__file__).parent.parent / "programs"


def run_program(name: str) -> list[int]:
    """Ассемблирует и выполняет программу, возвращает память."""
    program = read_program(str(PROGRAMS / name))
    machine = Machine(b"".join(encode(fields) for fields in program))
    machine.run()
    return machine.memory


def test_copy() -> None:
    """Массив 1100-1104 скопирован в 1200-1204, источник не изменился."""
    memory = run_program("copy.csv")
    assert memory[1100:1105] == [10, 20, 30, 40, 50]
    assert memory[1200:1205] == [10, 20, 30, 40, 50]
