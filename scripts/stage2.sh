#!/usr/bin/env sh
cd "$(dirname "$0")/.."
mkdir -p out

run() {
    echo
    echo "\$ ./run.sh $*"
    ./run.sh "$@"
    echo "код возврата: $?"
}

echo "===== программа с тестами из спецификации ====="
cat programs/spec.csv
run asm --input programs/spec.csv --output out/spec.bin --test

echo
echo "===== ожидается по спецификации ====="
echo "0xE0, 0x28, 0x80, 0x38, 0x00, 0x00, 0x00"
echo "0x5A, 0x62, 0xE0, 0x25, 0x00, 0x00, 0x00"
echo "0x8A, 0x0F, 0xA0, 0x01, 0x00, 0x00, 0x00"
echo "0x64, 0x2E, 0x00, 0x6E, 0xE0, 0x2C, 0x00"

echo
echo "===== содержимое двоичного файла ====="
od -A d -t x1 out/spec.bin

echo
echo "===== без режима тестирования ====="
run asm --input programs/spec.csv --output out/spec.bin

echo
echo "===== ошибки ====="
run asm --input programs/spec.csv --output nope/spec.bin
run asm --input nope.csv --output out/spec.bin
