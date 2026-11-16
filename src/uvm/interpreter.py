"""Интерпретатор УВМ: выполняет машинный код и сохраняет дамп памяти."""

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

from uvm.machine import MEMORY_SIZE, Machine
from uvm.spec import UvmError


def parse_range(text: str) -> tuple[int, int]:
    """Читает диапазон адресов вида «1000-1010», оба конца включены."""
    start, dash, end = text.partition("-")
    if not dash or not start.isdigit() or not end.isdigit():
        raise argparse.ArgumentTypeError(
            f"{text!r} is not a range like 1000-1010"
        )
    first, last = int(start), int(end)
    if first > last or last >= MEMORY_SIZE:
        raise argparse.ArgumentTypeError(
            f"range {text!r} must be within 0-{MEMORY_SIZE - 1}"
        )
    return first, last


def read_binary(path: str) -> bytes:
    """Читает машинный код из файла."""
    try:
        return Path(path).read_bytes()
    except OSError:
        raise UvmError(f"file {path!r} not found") from None


def make_dump(memory: list[int], first: int, last: int) -> ET.Element:
    """Собирает XML с содержимым ячеек от first до last."""
    root = ET.Element("memory", start=str(first), end=str(last))
    for address in range(first, last + 1):
        cell = ET.SubElement(root, "cell", address=str(address))
        cell.text = str(memory[address])
    ET.indent(root)
    return root


def save_dump(root: ET.Element, path: str) -> None:
    """Записывает дамп памяти в XML-файл."""
    try:
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    except OSError as error:
        raise UvmError(f"cannot write {path!r}: {error.strerror}") from None


def parse_arguments() -> argparse.Namespace:
    """Читает параметры командной строки."""
    parser = argparse.ArgumentParser(description="Интерпретатор УВМ")
    parser.add_argument(
        "--input", required=True, help="двоичный файл с программой"
    )
    parser.add_argument(
        "--dump", required=True, help="XML-файл для дампа памяти"
    )
    parser.add_argument(
        "--range",
        required=True,
        type=parse_range,
        help="адреса для дампа, например 1000-1010",
    )
    return parser.parse_args()


def main() -> int:
    """Запускает интерпретатор и возвращает код завершения."""
    args = parse_arguments()
    first, last = args.range
    try:
        machine = Machine(read_binary(args.input))
        count = machine.run()
        save_dump(make_dump(machine.memory, first, last), args.dump)
    except UvmError as error:
        print(f"error: {error}")
        return 1
    print(f"Executed {count} commands")
    print(f"Memory {first}-{last} saved to {args.dump}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
