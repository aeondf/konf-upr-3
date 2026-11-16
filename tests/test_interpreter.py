"""Тесты интерпретатора УВМ."""

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from uvm.assembler import parse_program
from uvm.interpreter import main, make_dump, parse_range
from uvm.spec import encode

ERROR_CODE = 1
FIRST = 1000
LAST = 1002


def write_program(path: Path, text: str) -> str:
    """Ассемблирует текст программы в файл и возвращает его путь."""
    program = parse_program(text, "test.csv")
    path.write_bytes(b"".join(encode(fields) for fields in program))
    return str(path)


def run_main(monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    """Запускает main() с заданными параметрами."""
    monkeypatch.setattr("sys.argv", ["interpreter.py", *argv])
    return main()


def test_parse_range() -> None:
    """Диапазон «1000-1002» — оба конца включены."""
    assert parse_range("1000-1002") == (FIRST, LAST)


@pytest.mark.parametrize("text", ["1000", "a-b", "-5", "10-5", "0-65536"])
def test_bad_range(text: str) -> None:
    """Неверный диапазон — ошибка argparse."""
    with pytest.raises(argparse.ArgumentTypeError):
        parse_range(text)


def test_make_dump() -> None:
    """Каждая ячейка — элемент cell с адресом и значением."""
    memory = [0] * 2000
    memory[1001] = 42
    root = make_dump(memory, FIRST, LAST)
    assert root.attrib == {"start": "1000", "end": "1002"}
    cells = {cell.get("address"): cell.text for cell in root}
    assert cells == {"1000": "0", "1001": "42", "1002": "0"}


def test_main_saves_dump(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Программа выполняется, дамп памяти сохраняется в XML."""
    binary = write_program(tmp_path / "p.bin", "const,1001,42\nconst,1002,7")
    dump = tmp_path / "dump.xml"
    argv = ("--input", binary, "--dump", str(dump), "--range", "1000-1002")
    assert run_main(monkeypatch, *argv) == 0
    cells = [cell.text for cell in ET.parse(dump).getroot()]
    assert cells == ["0", "42", "7"]
    assert capsys.readouterr().out == (
        f"Executed 2 commands\nMemory 1000-1002 saved to {dump}\n"
    )


def test_main_missing_file(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Файла с программой нет — сообщение и код 1."""
    argv = ("--input", "nope.bin", "--dump", "d.xml", "--range", "0-1")
    assert run_main(monkeypatch, *argv) == ERROR_CODE
    assert capsys.readouterr().out == "error: file 'nope.bin' not found\n"


def test_main_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Ошибка во время выполнения — сообщение и код 1."""
    binary = write_program(tmp_path / "p.bin", "const,7,1000\nconst,9,5")
    dump = str(tmp_path / "dump.xml")
    argv = ("--input", binary, "--dump", dump, "--range", "0-1")
    assert run_main(monkeypatch, *argv) == ERROR_CODE
    assert "does not hold a command" in capsys.readouterr().out
