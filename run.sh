#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
case "${1:-}" in
    asm) shift; exec uv run --quiet python src/uvm/assembler.py "$@" ;;
    vm) shift; exec uv run --quiet python src/uvm/interpreter.py "$@" ;;
    *) echo "usage: ./run.sh asm|vm ARGUMENTS" >&2; exit 2 ;;
esac
