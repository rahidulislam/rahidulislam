import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase

PROBE = "import rahidulislam.settings as s; print(s.DEBUG)"


class SettingsDefaultTests(SimpleTestCase):
    def run_settings(self, **env):
        clean = {k: v for k, v in os.environ.items() if not k.startswith("DJANGO_")}
        return subprocess.run(
            [sys.executable, "-c", PROBE],
            cwd=settings.BASE_DIR,
            env={**clean, **env},
            capture_output=True,
            text=True,
        )

    def test_debug_is_off_unless_explicitly_enabled(self):
        result = self.run_settings(DJANGO_SECRET_KEY="x" * 50)
        self.assertEqual(result.stdout.strip(), "False", result.stderr)
        self.assertEqual(self.run_settings(DJANGO_DEBUG="true").stdout.strip(), "True")

    def test_production_refuses_the_development_secret(self):
        result = self.run_settings()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_DEBUG=true", result.stderr)
