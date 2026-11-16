"""Ассемблер УВМ: текст программы в формате CSV → команды."""

import argparse
import csv
from pathlib import Path

from uvm.spec import COMMANDS, Field, UvmError

Fields = dict[str, int]


def parse_number(text: str, where: str) -> int:
    """Читает десятичное или шестнадцатеричное (0x...) число."""
    try:
        return int(text, 0)
    except ValueError:
        raise UvmError(f"{where}: {text!r} is not a number") from None


def parse_operand(field: Field, text: str, where: str) -> int:
    """Читает операнд и проверяет, что он помещается в своё поле."""
    value = parse_number(text, where)
    if not 0 <= value <= field.limit():
        raise UvmError(
            f"{where}: {field.name}={value} does not fit in bits "
            f"{field.first}-{field.last} (0..{field.limit()})"
        )
    return value


def parse_row(row: list[str], where: str) -> Fields:
    """Переводит строку «команда,операнды» в поля и значения."""
    name, *operands = row
    command = COMMANDS.get(name.lower())
    if command is None:
        raise UvmError(f"{where}: unknown command {name!r}")
    if len(operands) != len(command.fields):
        raise UvmError(
            f"{where}: {name} needs {len(command.fields)} operands, "
            f"got {len(operands)}"
        )
    fields = {"A": command.opcode}
    for field, text in zip(command.fields, operands, strict=True):
        fields[field.name] = parse_operand(field, text, where)
    return fields


def parse_program(text: str, name: str) -> list[Fields]:
    """Разбирает программу; пустые строки и строки с # пропускаются."""
    program = []
    reader = csv.reader(text.splitlines())
    for row in reader:
        cells = [cell.strip() for cell in row]
        if not cells or not cells[0] or cells[0].startswith("#"):
            continue
        program.append(parse_row(cells, f"{name}:{reader.line_num}"))
    if not program:
        raise UvmError(f"{name}: program has no commands")
    return program


def read_program(path: str) -> list[Fields]:
    """Читает программу из файла."""
    try:
        text = Path(path).read_text()
    except OSError:
        raise UvmError(f"file {path!r} not found") from None
    return parse_program(text, path)


def format_fields(fields: Fields) -> str:
    """Записывает команду как в спецификации: «A=0, B=327, C=452»."""
    return ", ".join(f"{name}={value}" for name, value in fields.items())


def parse_arguments() -> argparse.Namespace:
    """Читает параметры командной строки."""
    parser = argparse.ArgumentParser(description="Ассемблер УВМ")
    parser.add_argument(
        "--input", required=True, help="файл с текстом программы (CSV)"
    )
    parser.add_argument(
        "--output", required=True, help="двоичный файл-результат"
    )
    parser.add_argument(
        "--test", action="store_true", help="режим тестирования"
    )
    return parser.parse_args()


def main() -> int:
    """Запускает ассемблер и возвращает код завершения."""
    args = parse_arguments()
    try:
        program = read_program(args.input)
    except UvmError as error:
        print(f"error: {error}")
        return 1
    print(f"Commands: {len(program)}")
    if args.test:
        for fields in program:
            print(format_fields(fields))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
