"""Run the same backend gates locally and in CI."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    os.chdir(ROOT)
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
    # Production hashes static files; broken CSS url() references fail here.
    with tempfile.TemporaryDirectory() as static_root:
        command = [sys.executable, "manage.py", "collectstatic", "--noinput", "-v0"]
        print("+ DJANGO_STATIC_MANIFEST=true " + " ".join(command), flush=True)
        subprocess.run(
            command,
            check=True,
            env={
                **os.environ,
                "DJANGO_STATIC_MANIFEST": "true",
                "DJANGO_STATIC_ROOT": static_root,
            },
        )


if __name__ == "__main__":
    main()
