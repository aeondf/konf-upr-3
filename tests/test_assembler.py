"""Тесты ассемблера УВМ."""

from pathlib import Path

import pytest

from uvm.assembler import format_fields, main, parse_program, read_program
from uvm.spec import UvmError

SPEC = Path(__file__).parent.parent / "programs" / "spec.csv"
ERROR_CODE = 1


def run_main(monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    """Запускает main() с заданными параметрами."""
    monkeypatch.setattr("sys.argv", ["assembler.py", *argv])
    return main()


def test_spec_program() -> None:
    """Тесты из спецификации дают те же поля и значения."""
    assert read_program(str(SPEC)) == [
        {"A": 0, "B": 327, "C": 452},
        {"A": 26, "B": 786, "C": 303},
        {"A": 10, "B": 124, "C": 13},
        {"A": 4, "B": 371, "C": 880, "D": 359},
    ]


def test_format_fields() -> None:
    """Команда записывается полями, как в спецификации."""
    fields = {"A": 0, "B": 327, "C": 452}
    assert format_fields(fields) == "A=0, B=327, C=452"


def test_comments_spaces_and_hex() -> None:
    """Комментарии и пустые строки пропускаются, пробелы и 0x допустимы."""
    text = "# комментарий\n\n CONST , 0x10, 7\n"
    assert parse_program(text, "p.csv") == [{"A": 0, "B": 16, "C": 7}]


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("jump,1,2", "p.csv:1: unknown command 'jump'"),
        ("const,1", "p.csv:1: const needs 2 operands, got 1"),
        ("div,1,2,3,4", "p.csv:1: div needs 3 operands, got 4"),
        ("read,1,x", "p.csv:1: 'x' is not a number"),
        ("read,65536,1", "p.csv:1: B=65536 does not fit in bits 5-20"),
        ("const,1,4194304", "p.csv:1: C=4194304 does not fit in bits 21-42"),
        ("write,-1,1", "p.csv:1: B=-1 does not fit"),
    ],
)
def test_errors(line: str, message: str) -> None:
    """Ошибка в строке — сообщение с номером строки."""
    with pytest.raises(UvmError, match=message):
        parse_program(line, "p.csv")


def test_error_line_number() -> None:
    """Номер строки считается с учётом комментариев и пустых строк."""
    with pytest.raises(UvmError, match="p.csv:3:"):
        parse_program("# a\n\nbad,1\n", "p.csv")


def test_empty_program() -> None:
    """Программа без команд — ошибка."""
    with pytest.raises(UvmError, match="no commands"):
        parse_program("# только комментарий\n", "p.csv")


def test_missing_file() -> None:
    """Файла нет — понятная ошибка."""
    with pytest.raises(UvmError, match="not found"):
        read_program("nope.csv")


def test_main_test_mode(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """В режиме тестирования печатаются поля и значения команд."""
    argv = ("--input", str(SPEC), "--output", "spec.bin", "--test")
    assert run_main(monkeypatch, *argv) == 0
    assert capsys.readouterr().out == (
        "Commands: 4\n"
        "A=0, B=327, C=452\n"
        "A=26, B=786, C=303\n"
        "A=10, B=124, C=13\n"
        "A=4, B=371, C=880, D=359\n"
    )


def test_main_without_test_mode(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Без режима тестирования поля не печатаются."""
    run_main(monkeypatch, "--input", str(SPEC), "--output", "spec.bin")
    assert capsys.readouterr().out == "Commands: 4\n"


def test_main_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Ошибка — сообщение и код 1."""
    code = run_main(monkeypatch, "--input", "nope.csv", "--output", "x.bin")
    assert code == ERROR_CODE
    assert capsys.readouterr().out == "error: file 'nope.csv' not found\n"
