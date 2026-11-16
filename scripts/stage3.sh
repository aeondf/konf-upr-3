#!/usr/bin/env sh
cd "$(dirname "$0")/.."
mkdir -p out

run() {
    echo
    echo "\$ ./run.sh $*"
    ./run.sh "$@"
    echo "код возврата: $?"
}

echo "===== копирование массива 1100-1104 -> 1200-1204 ====="
cat programs/copy.csv
run asm --input programs/copy.csv --output out/copy.bin
run vm --input out/copy.bin --dump out/copy.xml --range 1100-1104
cat out/copy.xml
run vm --input out/copy.bin --dump out/copy.xml --range 1200-1204
cat out/copy.xml

echo
echo "===== ошибки ====="
run vm --input nope.bin --dump out/dump.xml --range 0-10
run vm --input out/copy.bin --dump out/dump.xml --range 10-5
run vm --input out/copy.bin --dump out/dump.xml --range 0-70000
run vm --input out/copy.bin --dump nope/dump.xml --range 0-10
printf 'const,1000,70000\nread,1000,1001\n' > out/bad.csv
run asm --input out/bad.csv --output out/bad.bin
run vm --input out/bad.bin --dump out/dump.xml --range 0-10
printf 'div,1000,1001,1002\n' > out/div.csv
run asm --input out/div.csv --output out/div.bin
run vm --input out/div.bin --dump out/dump.xml --range 0-10
