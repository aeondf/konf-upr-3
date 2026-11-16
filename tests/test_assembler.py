"""Тесты ассемблера УВМ."""

from pathlib import Path

import pytest

from uvm.assembler import format_bytes, main, parse_program, read_program
from uvm.spec import UvmError

SPEC = Path(__file__).parent.parent / "programs" / "spec.csv"
ERROR_CODE = 1
SPEC_BYTES = [
    *(0xE0, 0x28, 0x80, 0x38, 0x00, 0x00, 0x00),
    *(0x5A, 0x62, 0xE0, 0x25, 0x00, 0x00, 0x00),
    *(0x8A, 0x0F, 0xA0, 0x01, 0x00, 0x00, 0x00),
    *(0x64, 0x2E, 0x00, 0x6E, 0xE0, 0x2C, 0x00),
]


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


def test_format_bytes() -> None:
    """Байты записываются как в спецификации."""
    assert format_bytes(bytes([0xE0, 0x28, 0x00])) == "0xE0, 0x28, 0x00"


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


def test_main_writes_binary(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Машинный код записывается в файл, печатается его размер."""
    output = tmp_path / "spec.bin"
    argv = ("--input", str(SPEC), "--output", str(output))
    assert run_main(monkeypatch, *argv) == 0
    assert output.read_bytes() == bytes(SPEC_BYTES)
    assert capsys.readouterr().out == f"Size of {output}: 28 bytes\n"


def test_main_test_mode(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """В режиме тестирования печатаются байты каждой команды."""
    output = tmp_path / "spec.bin"
    argv = ("--input", str(SPEC), "--output", str(output), "--test")
    assert run_main(monkeypatch, *argv) == 0
    assert capsys.readouterr().out == (
        "0xE0, 0x28, 0x80, 0x38, 0x00, 0x00, 0x00\n"
        "0x5A, 0x62, 0xE0, 0x25, 0x00, 0x00, 0x00\n"
        "0x8A, 0x0F, 0xA0, 0x01, 0x00, 0x00, 0x00\n"
        "0x64, 0x2E, 0x00, 0x6E, 0xE0, 0x2C, 0x00\n"
        f"Size of {output}: 28 bytes\n"
    )


def test_main_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Ошибка — сообщение и код 1."""
    code = run_main(monkeypatch, "--input", "nope.csv", "--output", "x.bin")
    assert code == ERROR_CODE
    assert capsys.readouterr().out == "error: file 'nope.csv' not found\n"


def test_main_cannot_write(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Папки для результата нет — сообщение и код 1."""
    argv = ("--input", str(SPEC), "--output", "nope/spec.bin")
    assert run_main(monkeypatch, *argv) == ERROR_CODE
    assert capsys.readouterr().out.startswith("error: cannot write 'nope/")
