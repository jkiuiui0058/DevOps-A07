#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
cp "$ROOT"/source/{main.c,config.h,unused.h,Makefile} "$WORK/"
cd "$WORK"

printf '%s\n' '== baseline: clean build ==' 
make clean
make
printf 'baseline output: '
./app

printf '%s\n' '== MD: edit config.h, incremental build ==' 
printf '#define BASE 12\n' > config.h
make
printf 'MD incremental output: '
./app

printf '%s\n' '== MD: clean build after config.h edit ==' 
make clean
make
printf 'MD clean output: '
./app

printf '%s\n' '== RD: restore config.h, clean build, edit unused.h ==' 
printf '#define BASE 10\n' > config.h
make clean
make
sleep 1
printf '#define UNUSED 1\n' > unused.h
make --debug=b
printf 'RD incremental output: '
./app
