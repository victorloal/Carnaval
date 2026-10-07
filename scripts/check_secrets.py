#!/usr/bin/env python
"""Fail if a tracked file looks like it holds a secret (NFR-09, SEC-46).

It scans the files `git ls-files` reports — the tracked tree, not the working
copy — so a gitignored `.env` is ignored by construction. The patterns are
deliberately narrow: placeholders and environment lookups must not trip it.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    (
        "private key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "assigned secret",
        re.compile(
            r"(?i)(secret[_-]?key|api[_-]?key|access[_-]?token)"
            r"\s*[:=]\s*['\"][A-Za-z0-9/+_=.-]{16,}['\"]"
        ),
    ),
    ("assigned password", re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{8,}['\"]")),
    (
        "connection string with a password",
        re.compile(r"(?i)(postgres|postgresql|mysql|redis)://[^\s:/]+:[^\s@]+@"),
    ),
]

SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".pdf", ".woff", ".woff2"}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, check=True
    )
    return [Path(name) for name in result.stdout.decode("utf-8").split("\0") if name]


def main() -> int:
    findings: list[str] = []
    for path in tracked_files():
        if path.suffix.lower() in SKIP_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for label, pattern in PATTERNS:
                if pattern.search(line):
                    findings.append(f"{path}:{lineno}: {label}")

    if findings:
        print("Potential secrets in tracked files (NFR-09, SEC-46):")
        print("\n".join(findings))
        return 1
    print("No secrets found in tracked files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
