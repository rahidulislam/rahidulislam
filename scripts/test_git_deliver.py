"""Local integration tests: real Git repositories and a fake GitHub CLI."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("git-deliver.py")


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.env = {
            **os.environ,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
        }
        self.command("git", "init", "--bare", str(self.root / "remote.git"))
        self.command("git", "init", "-b", "dev")
        self.command("git", "config", "user.name", "Delivery test")
        self.command("git", "config", "user.email", "delivery@example.invalid")
        self.config = {
            "base": "dev",
            "remote": "origin",
            "checks": [[sys.executable, "-c", "print('check passed')"]],
        }
        (self.repo / ".git-deliver.json").write_text(json.dumps(self.config))
        (self.repo / "app.txt").write_text("initial\n")
        self.command("git", "add", ".")
        self.command("git", "commit", "-m", "Initial")
        self.command("git", "remote", "add", "origin", str(self.root / "remote.git"))
        self.command("git", "push", "-u", "origin", "dev")
        self.command("git", "switch", "-c", "codex/test")
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "with open(os.environ['GH_TEST_LOG'], 'a') as f: f.write(json.dumps(sys.argv[1:]) + '\\n')\n"
            "if sys.argv[1:3] == ['pr', 'list']: print(os.environ.get('GH_TEST_PRS', '[]'))\n"
            "elif sys.argv[1:3] == ['pr', 'create']: print('https://example.invalid/pr/1')\n"
        )
        gh.chmod(0o755)
        self.env.update(
            PATH=str(bin_dir) + os.pathsep + self.env["PATH"],
            GH_TEST_LOG=str(self.root / "gh.log"),
        )
        self.initial = self.command("git", "rev-parse", "HEAD").stdout.strip()

    def command(self, *args):
        return subprocess.run(
            args,
            cwd=self.repo,
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
        )

    def deliver(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=False,
            cwd=self.repo,
            env=self.env,
            text=True,
            capture_output=True,
        )

    def changed(self):
        (self.repo / "app.txt").write_text("fixed contact validation\n")

    def test_commit_push_create_and_idempotent_retry(self):
        self.changed()
        result = self.deliver("--all", "--message", "fix: preserve contact validation")
        self.assertEqual(result.returncode, 0, result.stderr)
        head = self.command("git", "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(head, self.initial)
        self.assertIn(
            head,
            self.command("git", "ls-remote", "origin", "refs/heads/codex/test").stdout,
        )
        self.env["GH_TEST_PRS"] = '[{"number":1,"url":"https://example.invalid/pr/1"}]'
        retry = self.deliver("--message", "fix: preserve contact validation")
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertEqual(self.command("git", "rev-parse", "HEAD").stdout.strip(), head)
        calls = [
            json.loads(line) for line in (self.root / "gh.log").read_text().splitlines()
        ]
        self.assertEqual(sum(call[:2] == ["pr", "create"] for call in calls), 1)
        self.assertFalse(any(call[:2] == ["pr", "merge"] for call in calls))

    def test_failed_check_does_not_commit_or_push(self):
        self.config["checks"] = [[sys.executable, "-c", "raise SystemExit(1)"]]
        (self.repo / ".git-deliver.json").write_text(json.dumps(self.config))
        self.changed()
        self.assertNotEqual(
            self.deliver("--all", "--message", "fix: broken check").returncode, 0
        )
        self.assertEqual(
            self.command("git", "rev-parse", "HEAD").stdout.strip(), self.initial
        )
        self.assertEqual(
            self.command("git", "ls-remote", "origin", "refs/heads/codex/test").stdout,
            "",
        )

    def test_secret_file_is_rejected_before_commit(self):
        (self.repo / ".env").write_text("SOME_SECRET=not-a-real-secret\n")
        result = self.deliver("--all", "--message", "feat: configure app")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Potential credential file", result.stderr)
        self.assertEqual(
            self.command("git", "rev-parse", "HEAD").stdout.strip(), self.initial
        )

    def test_protected_branch_rejected(self):
        self.command("git", "switch", "dev")
        self.changed()
        self.assertNotEqual(
            self.deliver("--all", "--message", "fix: task").returncode, 0
        )

    def test_plan_is_read_only(self):
        self.changed()
        before = self.command("git", "status", "--porcelain").stdout
        self.assertEqual(self.deliver("--plan", "--all").returncode, 0)
        self.assertEqual(self.command("git", "status", "--porcelain").stdout, before)
        self.assertFalse((self.root / "gh.log").exists())

    def test_unselected_work_prevents_commit(self):
        self.changed()
        (self.repo / "unrelated.txt").write_text("user work\n")
        result = self.deliver("--files", "app.txt", "--message", "fix: validation")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(
            self.command("git", "rev-parse", "HEAD").stdout.strip(), self.initial
        )
        self.assertEqual((self.repo / "unrelated.txt").read_text(), "user work\n")

    def test_start_uses_latest_base(self):
        result = self.deliver("--start", "feature-new-task")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.command("git", "branch", "--show-current").stdout.strip(),
            "codex/feature-new-task",
        )


if __name__ == "__main__":
    unittest.main()
