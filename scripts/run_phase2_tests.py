#!/usr/bin/env python3
"""Run deterministic Phase 2 and Phase 3 lab and challenge tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "docs"
LANGS = ("en", "pt", "fr")
LABS = ("004", "005", "007", "017", "018", "019", "022", "090", "092", "093", "095", "096", "098", "099", "100", "101")
CHALLENGES = ("009", "010", "011")
PHASE3_LABS = ("014", "023", "034", "040", "042", "102", "103", "104", "105", "106")
PHASE3_CHALLENGES = ("012",)


def run(directory: Path) -> None:
    tests = sorted(directory.glob("test*.py"))
    if tests:
        commands = [[sys.executable, "-m", "unittest", "discover", "-v"]]
    else:
        commands = [
            [sys.executable, path.name]
            for path in sorted(directory.glob("*.py"))
            if "unittest.main()" in path.read_text(encoding="utf-8")
        ]
    if not commands:
        raise SystemExit(f"No executable tests found in {directory}")
    for command in commands:
        result = subprocess.run(command, cwd=directory, check=False)
        if result.returncode:
            raise SystemExit(f"Tests failed in {directory}: {' '.join(command)}")


def main() -> None:
    count = 0
    for lang in LANGS:
        for lab_id in LABS:
            run(DOCS / lang / "labs" / f"lab-{lab_id}")
            count += 1
        for challenge_id in CHALLENGES:
            run(DOCS / lang / "challenges" / f"challenge-{challenge_id}")
            count += 1
        for lab_id in PHASE3_LABS:
            run(DOCS / lang / "labs" / f"lab-{lab_id}")
            count += 1
        for challenge_id in PHASE3_CHALLENGES:
            run(DOCS / lang / "challenges" / f"challenge-{challenge_id}")
            count += 1
    print(f"Passed {count} Phase 2 and Phase 3 test directories.")


if __name__ == "__main__":
    main()
