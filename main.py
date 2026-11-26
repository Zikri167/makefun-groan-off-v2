#!/usr/bin/env python3
"""GROAN-OFF v2 — one-line dad joke entry writer.

Deterministic, Python stdlib only. Writes the winning line to entry.txt
in the resolved output directory with NO trailing newline, then reads it
back and verifies the bytes match exactly.
"""

import hashlib
import os
import sys

LINE = "I asked my router for a joke, but it kept buffering the punchline."


def resolve_output_dir():
    """Output dir fallback chain: env vars, then /output, ./output, cwd."""
    for var in ("OUTPUT_DIR", "_OUTPUT_DIR", "MAKEFUN_OUTPUT_DIR"):
        value = os.environ.get(var)
        if value:
            return value
    for candidate in ("/output", "./output"):
        if os.path.isdir(candidate):
            return candidate
    return os.getcwd()


def main():
    line = LINE
    if not 1 <= len(line) <= 140:
        raise SystemExit(f"gate fail: length {len(line)} not in 1..140")
    if "\n" in line or "\r" in line:
        raise SystemExit("gate fail: entry must be a single line")
    expected = line.encode("utf-8")

    outdir = resolve_output_dir()
    if os.path.exists(outdir) and not os.path.isdir(outdir):
        raise SystemExit(f"gate fail: output dir {outdir!r} exists and is not a directory")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(line)
    with open(path, "rb") as f:
        raw = f.read()
    if raw.endswith(b"\n") or raw.endswith(b"\r"):
        raise SystemExit("verify fail: entry.txt has a trailing newline")
    if raw != expected:
        raise SystemExit("verify fail: entry.txt bytes differ from entry line")
    if raw.decode("utf-8") != line:
        raise SystemExit("verify fail: entry.txt text differs from entry line")
    digest = hashlib.sha256(raw).hexdigest()
    print(f"wrote {path} ({len(line)} chars) sha256={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
