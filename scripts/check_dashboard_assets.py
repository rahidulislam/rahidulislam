"""Verify production static collection into a disposable output directory."""

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rahidulislam.settings")


def main() -> None:
    import django
    from django.core.management import call_command
    from django.test import override_settings

    django.setup()
    with TemporaryDirectory(prefix="portfolio-static-") as directory:
        with override_settings(STATIC_ROOT=directory):
            call_command("collectstatic", interactive=False, verbosity=0)
        for name in (
            "css/branding.css",
            "img/favicon.svg",
            "dashboard/dashboard.css",
            "dashboard/dashboard.js",
            "vendor/htmx/htmx.min.js",
        ):
            collected = Path(directory, name)
            if not collected.is_file() or not collected.stat().st_size:
                raise SystemExit(f"Missing production asset: {name}")
    print("Production static collection verified (dashboard CSS, JavaScript and HTMX).")


if __name__ == "__main__":
    main()
