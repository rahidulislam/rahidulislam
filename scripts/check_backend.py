"""Run the same backend gates locally and in CI."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    os.chdir(ROOT)
    # Settings default to production (DEBUG off). The gate runs the test suite
    # in development mode unless the caller chose otherwise.
    os.environ.setdefault("DJANGO_DEBUG", "true")
    commands = [
        [sys.executable, "-m", "ruff", "check", "."],
        [sys.executable, "-m", "black", "--check", "."],
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts",
            "-p",
            "test_git_deliver.py",
        ],
        [sys.executable, "manage.py", "check"],
        [sys.executable, "manage.py", "makemigrations", "--check", "--dry-run"],
        [sys.executable, "manage.py", "test", "--noinput"],
    ]
    for command in commands:
        print("+ " + " ".join(command), flush=True)
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
