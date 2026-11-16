"""Тесты готовых программ из папки programs."""

from pathlib import Path

import pytest

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


def test_div() -> None:
    """Частные целые, остаток отбрасывается."""
    memory = run_program("div.csv")
    assert memory[1200:1205] == [14, 9, 0, 1398101, 42]


@pytest.mark.parametrize(
    ("name", "x", "y", "z"),
    [
        (
            "vectors_1.csv",
            [100, 81, 50, 7, 1000],
            [10, 9, 7, 7, 3],
            [10, 9, 7, 1, 333],
        ),
        (
            "vectors_2.csv",
            [15, 27, 64, 99, 128],
            [3, 4, 8, 11, 16],
            [5, 6, 8, 9, 8],
        ),
        (
            "vectors_3.csv",
            [4194303, 1000000, 65536, 12345, 999],
            [1, 1000, 256, 5, 1000],
            [4194303, 1000, 256, 2469, 0],
        ),
    ],
)
def test_vectors(name: str, x: list[int], y: list[int], z: list[int]) -> None:
    """Z = X / Y поэлементно, X и Y не меняются."""
    memory = run_program(name)
    assert memory[1100:1105] == x
    assert memory[1105:1110] == y
    assert memory[1110:1115] == z
