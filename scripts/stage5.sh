#!/usr/bin/env sh
cd "$(dirname "$0")/.."
mkdir -p out

run() {
    echo
    echo "\$ ./run.sh $*"
    ./run.sh "$@"
    echo "код возврата: $?"
}

for number in 1 2 3; do
    name="vectors_$number"
    echo
    echo "===== пример $number: programs/$name.csv ====="
    grep -E '^# (X |Y |Ожидается)' "programs/$name.csv"
    run asm --input "programs/$name.csv" --output "out/$name.bin"
    run vm --input "out/$name.bin" --dump "out/$name.xml" --range 1100-1114
    cat "out/$name.xml"
done
