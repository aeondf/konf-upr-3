"""Учебная виртуальная машина: общая память и выполнение команд."""

from collections.abc import Callable

from uvm.spec import COMMAND_SIZE, COMMANDS, UvmError, decode

MEMORY_SIZE = 1 << 16

Fields = dict[str, int]


class Machine:
    """УВМ: команды и данные лежат в одной памяти."""

    def __init__(self, code: bytes) -> None:
        """Кладёт программу в память, начиная с адреса 0."""
        if len(code) % COMMAND_SIZE:
            raise UvmError(
                f"program size {len(code)} is not a multiple of {COMMAND_SIZE}"
            )
        if len(code) > MEMORY_SIZE:
            raise UvmError("program does not fit in memory")
        self.memory = [0] * MEMORY_SIZE
        self.memory[: len(code)] = code
        self.code_size = len(code)
        self.handlers: dict[int, Callable[[Fields], None]] = {
            COMMANDS["const"].opcode: self.load_const,
            COMMANDS["read"].opcode: self.read,
            COMMANDS["write"].opcode: self.write,
            COMMANDS["div"].opcode: self.divide,
        }

    def run(self) -> int:
        """Выполняет команды по порядку и возвращает их число."""
        addresses = range(0, self.code_size, COMMAND_SIZE)
        for address in addresses:
            self.step(address)
        return len(addresses)

    def step(self, address: int) -> None:
        """Читает команду из памяти, переводит в поля и выполняет."""
        fields = decode(self.fetch(address))
        self.handlers[fields["A"]](fields)

    def fetch(self, address: int) -> bytes:
        """Берёт из памяти 7 байт команды."""
        try:
            return bytes(self.memory[address : address + COMMAND_SIZE])
        except ValueError:
            raise UvmError(
                f"address {address}: memory does not hold a command"
            ) from None

    def get(self, address: int) -> int:
        """Возвращает значение ячейки памяти."""
        self.check(address)
        return self.memory[address]

    def set(self, address: int, value: int) -> None:
        """Записывает значение в ячейку памяти."""
        self.check(address)
        self.memory[address] = value

    def check(self, address: int) -> None:
        """Проверяет, что адрес есть в памяти."""
        if not 0 <= address < MEMORY_SIZE:
            raise UvmError(f"address {address} is outside memory")

    def load_const(self, fields: Fields) -> None:
        """Команда const: память[B] = C."""
        self.set(fields["B"], fields["C"])

    def read(self, fields: Fields) -> None:
        """Команда read: память[C] = память[память[B]]."""
        self.set(fields["C"], self.get(self.get(fields["B"])))

    def write(self, fields: Fields) -> None:
        """Команда write: память[память[C]] = память[B]."""
        self.set(self.get(fields["C"]), self.get(fields["B"]))

    def divide(self, fields: Fields) -> None:
        """Команда div: память[D] = память[память[B]] / память[C]."""
        divisor = self.get(fields["C"])
        if divisor == 0:
            raise UvmError(f"division by zero: cell {fields['C']} is 0")
        self.set(fields["D"], self.get(self.get(fields["B"])) // divisor)
