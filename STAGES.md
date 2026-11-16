# Этапы по коммитам

Каждый этап заканчивается отдельным коммитом. Переключиться на конец
этапа и вернуться обратно:

```sh
git checkout 3eb7639   # этап 1
git checkout abaa8ec   # этап 2
git checkout d108bef   # этап 3
git checkout 11c4e92   # этап 4
git checkout 94a154d   # этап 5
git checkout main      # вернуться к последней версии
```

После переключения просто запускайте `./run.sh` — `uv` сам поставит
зависимости. Перед переключением не должно быть незакоммиченных
изменений. Результаты (`.bin`, `.xml`) удобно складывать в папку `out/`:

```sh
mkdir -p out
```

| Этап | Коммит | Что нового |
|---|---|---|
| 1 | `3eb7639` | ассемблер: CSV → поля команд, в режиме теста печатает `A=0, B=327, C=452` |
| 2 | `abaa8ec` | ассемблер: поля → 7 байт машинного кода, файл `.bin`, размер, в режиме теста — байты |
| 3 | `d108bef` | интерпретатор: общая память, команды `const`, `read`, `write`, дамп в XML, копирование массива |
| 4 | `11c4e92` | интерпретатор: команда `div` (деление), программа с делениями |
| 5 | `94a154d` | тестовая задача: деление векторов, три примера |

---

## Этап 1. Перевод программы в промежуточное представление

```sh
git checkout 3eb7639
```

| Коммит | Что сделано |
|---|---|
| `10de322` | заготовка проекта: `pyproject.toml`, `run.sh`, ruff, pytest |
| `44acf3e` | `spec.py` — команды УВМ и их битовые поля |
| `a38ec42` | `assembler.py` — разбор CSV в поля и значения, `programs/spec.csv` |
| `3eb7639` | README (язык ассемблера) и `scripts/stage1.sh` |

**Как запустить:**

```sh
./run.sh asm --input programs/spec.csv --output out/spec.bin --test
sh scripts/stage1.sh
```

**Что видно** — внутреннее представление, как в тестах спецификации:

```
Commands: 4
A=0, B=327, C=452
A=26, B=786, C=303
A=10, B=124, C=13
A=4, B=371, C=880, D=359
```

Двоичный файл на этом этапе ещё не создаётся.

---

## Этап 2. Формирование машинного кода

```sh
git checkout abaa8ec
```

| Коммит | Что сделано |
|---|---|
| `545edea` | `spec.py` — функция `encode`: поля → 7 байт |
| `bf13def` | ассемблер записывает `.bin`, печатает размер, в режиме теста — байты |
| `abaa8ec` | README и `scripts/stage2.sh` |

**Как запустить:**

```sh
./run.sh asm --input programs/spec.csv --output out/spec.bin --test
./run.sh asm --input programs/spec.csv --output out/spec.bin
sh scripts/stage2.sh
```

**Что видно** — байты совпадают с тестами спецификации:

```
0xE0, 0x28, 0x80, 0x38, 0x00, 0x00, 0x00
0x5A, 0x62, 0xE0, 0x25, 0x00, 0x00, 0x00
0x8A, 0x0F, 0xA0, 0x01, 0x00, 0x00, 0x00
0x64, 0x2E, 0x00, 0x6E, 0xE0, 0x2C, 0x00
Size of out/spec.bin: 28 bytes
```

Печать полей (`A=0, B=327, ...`) убрана — по заданию она нужна была
только на этапе 1.

---

## Этап 3. Интерпретатор и операции с памятью

```sh
git checkout d108bef
```

| Коммит | Что сделано |
|---|---|
| `94fd84b` | `spec.py` — функция `decode`: 7 байт → поля |
| `5ea3775` | `machine.py` — общая память и команды `const`, `read`, `write` |
| `738f553` | `interpreter.py` — запуск и дамп памяти в XML |
| `fb42df8` | исправление: понятная ошибка для диапазона вида `10-5` |
| `13ce11d` | `programs/copy.csv` — копирование массива |
| `d108bef` | README и `scripts/stage3.sh` |

**Как запустить:**

```sh
./run.sh asm --input programs/copy.csv --output out/copy.bin
./run.sh vm --input out/copy.bin --dump out/copy.xml --range 1200-1204
cat out/copy.xml
sh scripts/stage3.sh
```

**Что видно** — массив 1100—1104 скопирован в 1200—1204:

```
Executed 25 commands
Memory 1200-1204 saved to out/copy.xml
```

```xml
<memory start="1200" end="1204">
  <cell address="1200">10</cell>
  <cell address="1201">20</cell>
  <cell address="1202">30</cell>
  <cell address="1203">40</cell>
  <cell address="1204">50</cell>
</memory>
```

Команда `div` на этом этапе выдаёт
`error: address 0: command A=4 is not supported yet`.

---

## Этап 4. АЛУ: деление

```sh
git checkout 11c4e92
```

| Коммит | Что сделано |
|---|---|
| `6e6d4ce` | `machine.py` — команда `div`, деление на ноль — ошибка |
| `f8d91c1` | `programs/div.csv` — пять делений |
| `11c4e92` | README и `scripts/stage4.sh` |

**Как запустить:**

```sh
./run.sh asm --input programs/div.csv --output out/div.bin
./run.sh vm --input out/div.bin --dump out/div.xml --range 1200-1204
cat out/div.xml
sh scripts/stage4.sh
```

**Что видно** — 100/7, 81/9, 5/10, 4194303/3, 42/1:

```xml
<memory start="1200" end="1204">
  <cell address="1200">14</cell>
  <cell address="1201">9</cell>
  <cell address="1202">0</cell>
  <cell address="1203">1398101</cell>
  <cell address="1204">42</cell>
</memory>
```

---

## Этап 5. Тестовая задача: деление векторов

```sh
git checkout 94a154d
```

| Коммит | Что сделано |
|---|---|
| `83a918f` | `programs/vectors_1.csv`, `vectors_2.csv`, `vectors_3.csv` и тесты к ним |
| `94a154d` | README и `scripts/stage5.sh` |

**Как запустить** (`X` — 1100—1104, `Y` — 1105—1109, `Z` — 1110—1114):

```sh
./run.sh asm --input programs/vectors_1.csv --output out/vectors_1.bin
./run.sh vm --input out/vectors_1.bin --dump out/vectors_1.xml --range 1100-1114
cat out/vectors_1.xml
./run.sh asm --input programs/vectors_2.csv --output out/vectors_2.bin
./run.sh vm --input out/vectors_2.bin --dump out/vectors_2.xml --range 1110-1114
./run.sh asm --input programs/vectors_3.csv --output out/vectors_3.bin
./run.sh vm --input out/vectors_3.bin --dump out/vectors_3.xml --range 1110-1114
sh scripts/stage5.sh
```

**Что видно** — ячейки 1110—1114 (`Z`):

| Пример | `X` | `Y` | `Z` |
|---|---|---|---|
| 1 | 100, 81, 50, 7, 1000 | 10, 9, 7, 7, 3 | 10, 9, 7, 1, 333 |
| 2 | 15, 27, 64, 99, 128 | 3, 4, 8, 11, 16 | 5, 6, 8, 9, 8 |
| 3 | 4194303, 1000000, 65536, 12345, 999 | 1, 1000, 256, 5, 1000 | 4194303, 1000, 256, 2469, 0 |

---

## Тесты и линтер на любом этапе

```sh
uv run pytest
uv run ruff check src tests
```
