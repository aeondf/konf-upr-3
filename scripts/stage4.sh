#!/usr/bin/env sh
cd "$(dirname "$0")/.."
mkdir -p out

run() {
    echo
    echo "\$ ./run.sh $*"
    ./run.sh "$@"
    echo "код возврата: $?"
}

echo "===== деление ====="
cat programs/div.csv
run asm --input programs/div.csv --output out/div.bin
run vm --input out/div.bin --dump out/div.xml --range 1200-1204
cat out/div.xml

echo
echo "===== ожидается ====="
echo "1200: 100 / 7 = 14"
echo "1201: 81 / 9 = 9"
echo "1202: 5 / 10 = 0"
echo "1203: 4194303 / 3 = 1398101"
echo "1204: 42 / 1 = 42"

echo
echo "===== ошибка: деление на ноль ====="
printf 'const,1100,5\nconst,1000,1100\ndiv,1000,1110,1200\n' > out/zero.csv
cat out/zero.csv
run asm --input out/zero.csv --output out/zero.bin
run vm --input out/zero.bin --dump out/zero.xml --range 1200-1200
