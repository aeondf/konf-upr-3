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
echo "A=0, B=327, C=452"
echo "A=26, B=786, C=303"
echo "A=10, B=124, C=13"
echo "A=4, B=371, C=880, D=359"

echo
echo "===== без режима тестирования ====="
run asm --input programs/spec.csv --output out/spec.bin

echo
echo "===== ошибки ====="
printf 'jump,1,2\n' > out/bad.csv
run asm --input out/bad.csv --output out/bad.bin
printf 'const,1\n' > out/bad.csv
run asm --input out/bad.csv --output out/bad.bin
printf 'const,1,4194304\n' > out/bad.csv
run asm --input out/bad.csv --output out/bad.bin
printf 'read,1,x\n' > out/bad.csv
run asm --input out/bad.csv --output out/bad.bin
run asm --input nope.csv --output out/bad.bin
run asm --input programs/spec.csv
