#!/usr/bin/env bash
set -euo pipefail

OUTPUT=/lab/output
B_WORK=/tmp/e3-b-restored
TRACE_WORK=/tmp/e3-trace

rm -rf "$OUTPUT" "$B_WORK" "$TRACE_WORK"

mkdir -p \
  "$OUTPUT/environment" \
  "$OUTPUT/md-rd" \
  "$OUTPUT/incremental" \
  "$OUTPUT/contract-validation" \
  "$OUTPUT/linux-trace"

echo "=== COLLECT ENVIRONMENT ==="

{
  echo "=== OS ==="
  cat /etc/os-release
  echo
  echo "=== KERNEL ==="
  uname -a
  echo
  echo "=== ARCH ==="
  uname -m
  echo
  echo "=== GCC ==="
  gcc --version
  echo
  echo "=== MAKE ==="
  make --version
  echo
  echo "=== GIT ==="
  git --version
  echo
  echo "=== PYTHON ==="
  python3 --version
  echo
  echo "=== STRACE ==="
  strace -V
} > "$OUTPUT/environment/tool-versions.txt" 2>&1

echo "=== RUN A MD/RD ==="

(
  cd /lab/A
  ./run-experiments.sh
) > "$OUTPUT/md-rd/replay.log" 2>&1

echo "0" > "$OUTPUT/md-rd/exit-code.txt"

echo "=== RESTORE B BUNDLE ==="

git clone /lab/B/repository.bundle "$B_WORK" \
  > "$OUTPUT/incremental/bundle-clone.log" 2>&1

git -C "$B_WORK" bundle verify /lab/B/repository.bundle \
  > "$OUTPUT/incremental/bundle-verify.log" 2>&1

cd "$B_WORK"

{
  echo "C0=$(git rev-parse C0)"
  echo "C1=$(git rev-parse C1)"
  echo "C2=$(git rev-parse C2)"
} > "$OUTPUT/incremental/commit-map.txt"

git log --oneline --decorate --all --graph \
  > "$OUTPUT/incremental/git-history.txt"

git diff C0 C1 \
  > "$OUTPUT/incremental/C0-C1.diff"

git diff C1 C2 \
  > "$OUTPUT/incremental/C1-C2.diff"

echo "=== RUN B C0/C1/C2 ==="

{
  echo "=== C0 CLEAN BUILD ==="
  git checkout C0
  echo "commit=$(git rev-parse HEAD)"
  make clean
  make
  echo -n "C0 output="
  ./app

  echo "=== C1 CLEAN BUILD ==="
  git checkout C1
  echo "commit=$(git rev-parse HEAD)"
  make clean
  make
  echo -n "C1 clean output="
  ./app

  echo "=== C1 MISSING DEPENDENCY ==="
  sleep 1
  sed -i 's/FEATURE 2/FEATURE 3/' feature.h
  echo -n "feature.h="
  cat feature.h
  make
  echo -n "C1 incremental output="
  ./app
  git restore feature.h

  echo "=== PREPARE C1 OLD ARTIFACT ==="
  git checkout C1
  make clean
  make
  echo -n "C1 old artifact output="
  ./app

  echo "=== C2 INCREMENTAL WITHOUT CLEAN ==="
  git checkout C2
  echo "commit=$(git rev-parse HEAD)"
  make
  echo -n "C2 incremental output="
  ./app

  echo "=== C2 CLEAN BUILD ==="
  make clean
  make
  echo -n "C2 clean output="
  ./app
} > "$OUTPUT/incremental/replay.log" 2>&1

git checkout C1
make -n -B main.o \
  > "$OUTPUT/incremental/C1-command.txt"

git checkout C2
make -n -B main.o \
  > "$OUTPUT/incremental/C2-command.txt"

diff -u \
  "$OUTPUT/incremental/C1-command.txt" \
  "$OUTPUT/incremental/C2-command.txt" \
  > "$OUTPUT/incremental/command-diff.txt" || true

echo "0" > "$OUTPUT/incremental/exit-code.txt"

echo "=== VALIDATE CONTRACTS ==="

cd /lab

python3 scripts/validate_contracts.py \
  > "$OUTPUT/contract-validation/validate-contracts.log" 2>&1

echo "0" \
  > "$OUTPUT/contract-validation/exit-code.txt"

echo "=== COLLECT STRACE EVIDENCE ==="

cp -a /lab/A/source "$TRACE_WORK"

cd "$TRACE_WORK"

make clean \
  > "$OUTPUT/linux-trace/clean.log" 2>&1

strace -ff \
  -o "$OUTPUT/linux-trace/trace.log" \
  -e trace=%file,%process \
  make \
  > "$OUTPUT/linux-trace/make.stdout.log" \
  2> "$OUTPUT/linux-trace/make.stderr.log"

grep -H "config.h" "$OUTPUT"/linux-trace/trace.log* \
  > "$OUTPUT/linux-trace/config-h-access.txt" || true

make -pn \
  > "$OUTPUT/linux-trace/make-database.txt" 2>&1

echo "=== CREATE CHECKSUMS ==="

cd "$OUTPUT"

find . -type f ! -name SHA256SUMS \
  -print0 | sort -z | xargs -0 sha256sum \
  > SHA256SUMS

sha256sum -c SHA256SUMS \
  > checksum-validation.txt

echo "=== ALL UNIFIED CHECKS PASSED ==="
