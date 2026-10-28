#!/usr/bin/env python3
"""Check, commit, push and open a GitHub PR. Python standard library only."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CONFIG = ".git-deliver.json"
PROTECTED = {"main", "master", "dev", "develop", "staging", "production"}


def run(argv, root, capture=False, check=True):
    if not capture:
        print("+ " + " ".join(argv), flush=True)
    return subprocess.run(
        argv,
        cwd=root,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )


def git(root, *args):
    return run(["git", *args], root, capture=True).stdout.strip()


def fail(message):
    raise ValueError(message)


def validate_config(config):
    for key in ("base", "remote"):
        value = config.get(key)
        if not isinstance(value, str) or not value or value.startswith("-"):
            fail(f"Set a valid {key!r} in {CONFIG}.")
    checks = config.get("checks")
    if not isinstance(checks, list) or not checks:
        fail(f"Configure at least one real validation command in {CONFIG} checks.")
    if any(
        not isinstance(command, list)
        or not command
        or any(not isinstance(arg, str) or not arg for arg in command)
        for command in checks
    ):
        fail("Each check must be an array of command arguments, not a shell string.")


def guard_staged(root):
    names = git(root, "diff", "--cached", "--name-only", "-z").split("\0")
    for name in filter(None, names):
        path = Path(name)
        if (
            (
                path.name.startswith(".env")
                and path.name not in {".env.example", ".env.sample", ".env.template"}
            )
            or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}
            or path.name in {"id_rsa", "id_ed25519", "credentials"}
            or ".aws" in path.parts
        ):
            fail(f"Potential credential file staged: {name}. Unstage it and review.")
    diff = git(root, "diff", "--cached", "--no-ext-diff", "--unified=0")
    additions = "\n".join(
        line
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    if re.search(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bgh[pousr]_[A-Za-z0-9]{20,}\b",
        additions,
    ):
        fail(
            "Potential secret detected in staged additions. Review locally; no content was printed."
        )


def initialize(root, base):
    path = root / CONFIG
    if path.exists():
        fail(f"{path} already exists; edit it instead of overwriting.")
    checks = []
    if (root / "scripts/check_backend.py").exists():
        checks = [["python", "scripts/check_backend.py"]]
    elif (root / "package.json").exists():
        scripts = json.loads((root / "package.json").read_text()).get("scripts", {})
        manager = (
            "pnpm"
            if (root / "pnpm-lock.yaml").exists()
            else "yarn" if (root / "yarn.lock").exists() else "npm"
        )
        checks = [
            [manager, "run", name]
            for name in ("lint", "typecheck", "test", "build")
            if name in scripts
        ]
    path.write_text(
        json.dumps(
            {"base": base or "dev", "remote": "origin", "checks": checks}, indent=2
        )
        + "\n"
    )
    print(f"Created {path}. Review the base branch and checks before running delivery.")
    if not checks:
        print(
            "No check commands detected. Add your project's actual test/lint commands."
        )


def github_repo(root, remote):
    repository = git(root, "remote", "get-url", remote)
    ssh_remote = re.fullmatch(r"[^@]+@([^:]+):(.+)", repository)
    if ssh_remote:
        repository = "https://" + ssh_remote[1] + "/" + ssh_remote[2]
    return repository.removesuffix(".git")


def promote(root, config, args):
    if args.init or args.start or args.base or args.files or args.all or args.message:
        fail(
            "--promote cannot be combined with init/start/base/message/file selection."
        )
    routes = config.get("promotions", {})
    if not isinstance(routes, dict):
        fail("promotions must map target branches to their source branches.")
    source = routes.get(args.promote)
    target = args.promote
    if (
        not isinstance(source, str)
        or not source
        or source.startswith("-")
        or source == target
    ):
        fail(
            f"Configure promotions.{target} with the permitted source branch in {CONFIG}."
        )
    if args.plan:
        print(
            json.dumps(
                {
                    "source": source,
                    "target": target,
                    "remote": config["remote"],
                    "action": "create or reuse promotion PR; CI validates remote commits",
                },
                indent=2,
            )
        )
        return
    run(["git", "check-ref-format", "--branch", source], root)
    run(["git", "check-ref-format", "--branch", target], root)
    remote = config["remote"]
    run(["gh", "auth", "status"], root)
    run(["git", "fetch", remote, source, target], root)
    repository = github_repo(root, remote)
    prs = json.loads(
        run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repository,
                "--base",
                target,
                "--head",
                source,
                "--state",
                "open",
                "--json",
                "number,url",
            ],
            root,
            capture=True,
        ).stdout
    )
    if prs:
        print("Existing promotion PR: " + prs[0]["url"])
        return
    comparison = f"{remote}/{target}..{remote}/{source}"
    commits = git(root, "log", "--format=- %s", comparison)
    difference = run(
        ["git", "diff", "--quiet", f"{remote}/{target}", f"{remote}/{source}"],
        root,
        capture=True,
        check=False,
    )
    if difference.returncode not in (0, 1):
        fail("Unable to compare promotion branches.")
    if not commits or difference.returncode == 0:
        fail("No new content to promote; no PR was created.")
    title = args.title or f"Promote {source} to {target}"
    body = (
        args.body_file.resolve().read_text()
        if args.body_file
        else (
            f"Promote `{source}` to `{target}` for release validation.\n\n"
            f"Source commit: `{git(root, 'rev-parse', f'{remote}/{source}')}`\n\n"
            f"Changes:\n{commits}\n\n"
            "Validation: this PR must pass repository CI before merge. "
            "No local changes were committed or pushed; staging/production validation remains pending."
        )
    )
    command = [
        "gh",
        "pr",
        "create",
        "--repo",
        repository,
        "--base",
        target,
        "--head",
        source,
        "--title",
        title,
        "--body",
        body,
    ]
    if args.draft:
        command.append("--draft")
    run(command, root)
    print("Promotion PR created. It has not been merged or deployed.")


def is_ancestor(root, before, after):
    result = run(
        ["git", "merge-base", "--is-ancestor", before, after],
        root,
        capture=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        fail("Unable to compare branch ancestry.")
    return result.returncode == 0


def sync_branches(root, config, args):
    if (
        args.init
        or args.start
        or args.promote
        or args.base
        or args.files
        or args.all
        or args.message
        or args.title
        or args.body_file
        or args.draft
    ):
        fail("--sync cannot be combined with delivery or promotion flags.")
    branches = args.sync if args.sync else config.get("sync_branches", [config["base"]])
    if (
        not isinstance(branches, list)
        or not branches
        or any(
            not isinstance(branch, str) or not branch or branch.startswith("-")
            for branch in branches
        )
    ):
        fail("sync_branches must be a nonempty list of branch names.")
    if len(set(branches)) != len(branches):
        fail("Each sync branch must be specified once.")
    if args.sync_source and len(branches) != 1:
        fail(
            "--sync-source requires exactly one target: --sync dev --sync-source staging."
        )
    if args.push_sync and not args.sync_source:
        fail(
            "--push-sync requires an explicit --sync-source and a single target branch."
        )
    source_branches = list(
        dict.fromkeys([*branches, *([args.sync_source] if args.sync_source else [])])
    )
    for branch in source_branches:
        if not isinstance(branch, str) or branch.startswith("-"):
            fail("Invalid sync source branch.")
        git(root, "check-ref-format", "--branch", branch)
    remote = config["remote"]
    if args.plan:
        print(
            json.dumps(
                {
                    "targets": branches,
                    "source": args.sync_source or "matching remote branches",
                    "remote": remote,
                    "push": args.push_sync,
                    "policy": "fast-forward only; no stash, reset, checkout switch, force push, or protection bypass",
                },
                indent=2,
            )
        )
        return
    for operation in (
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "rebase-merge",
        "rebase-apply",
    ):
        if (root / git(root, "rev-parse", "--git-path", operation)).exists():
            fail("Finish or abort the current Git operation before syncing.")
    if git(root, "diff", "--name-only", "--diff-filter=U"):
        fail("Resolve current conflicts before syncing.")
    run(
        [
            "git",
            "fetch",
            "--no-tags",
            remote,
            *[
                f"refs/heads/{branch}:refs/remotes/{remote}/{branch}"
                for branch in source_branches
            ],
        ],
        root,
    )
    current = git(root, "branch", "--show-current")
    occupied = {}
    location = None
    for line in git(root, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            location = Path(line.removeprefix("worktree ")).resolve()
        elif line.startswith("branch refs/heads/"):
            occupied[line.removeprefix("branch refs/heads/")] = location
    plans = []
    for branch in branches:
        if branch in occupied and occupied[branch] != root.resolve():
            fail(
                f"{branch} is checked out in another worktree: {occupied[branch]}. Run --repo there."
            )
        remote_target = git(root, "rev-parse", f"refs/remotes/{remote}/{branch}")
        desired = git(
            root, "rev-parse", f"refs/remotes/{remote}/{args.sync_source or branch}"
        )
        exists = run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
            root,
            capture=True,
            check=False,
        )
        if exists.returncode not in (0, 1):
            fail(f"Unable to read local branch {branch}.")
        before = (
            git(root, "rev-parse", f"refs/heads/{branch}")
            if exists.returncode == 0
            else None
        )
        if before and not is_ancestor(root, before, desired):
            fail(
                f"{branch} is ahead of or diverged from the sync source. No local branches were changed; review its commits. No reset or force push was attempted."
            )
        if args.sync_source and not is_ancestor(root, remote_target, desired):
            fail(
                "Remote target cannot fast-forward to the requested source. No local branches were changed."
            )
        if (
            branch == current
            and before != desired
            and git(root, "status", "--porcelain")
        ):
            if git(root, "rev-parse", f"{before}^{{tree}}") != git(
                root, "rev-parse", f"{desired}^{{tree}}"
            ):
                fail(
                    f"{branch} has local changes and its tree would change. Preserve your work or use an isolated worktree. Nothing was stashed or reset."
                )
        plans.append((branch, before, desired))
    # Preflight every branch before changing any local ref. Git commands retain
    # their own locks and compare-and-swap / fast-forward checks for races.
    for branch, before, desired in plans:
        if before == desired:
            print(f"{branch}: already synced at {desired[:12]}")
        elif branch == current:
            run(["git", "merge", "--ff-only", desired], root)
            print(f"{branch}: synced at {desired[:12]}")
        elif before is None:
            run(["git", "branch", branch, desired], root)
            run(["git", "branch", f"--set-upstream-to={remote}/{branch}", branch], root)
            print(f"{branch}: created at {desired[:12]}")
        else:
            run(["git", "update-ref", f"refs/heads/{branch}", desired, before], root)
            print(f"{branch}: synced at {desired[:12]}")
    if args.push_sync:
        result = run(
            [
                "git",
                "push",
                remote,
                f"{plans[0][2]}:refs/heads/{branches[0]}",
            ],
            root,
            check=False,
        )
        if result.returncode:
            fail(
                "Normal sync push was rejected. Local sync remains saved; remote was not bypassed. For PR-only branches, a protected sync PR may be required; it may add a merge commit rather than make both SHA values identical."
            )
    print(
        "Sync complete. Local edits and the active checkout were preserved; no PR was merged."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", default=".", help="Any directory within the repository"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create project configuration; no commit/push",
    )
    parser.add_argument(
        "--promote",
        choices=("staging", "main"),
        help="Create/reuse the configured release promotion PR",
    )
    parser.add_argument(
        "--sync",
        nargs="*",
        metavar="BRANCH",
        help="Fast-forward local branches from remote (defaults to sync_branches)",
    )
    parser.add_argument(
        "--sync-source",
        metavar="BRANCH",
        help="Use this remote branch as the source for one --sync target",
    )
    parser.add_argument(
        "--push-sync",
        action="store_true",
        help="Explicit normal push after --sync-source; protections are honored",
    )
    parser.add_argument("--base", help="PR target branch; also used by --start")
    parser.add_argument(
        "--start",
        metavar="TASK",
        help="Create codex/TASK from the latest base, then exit",
    )
    parser.add_argument(
        "--message",
        help="Specific commit message, e.g. fix: preserve contact form values",
    )
    parser.add_argument("--title", help="PR title; defaults to the commit message")
    parser.add_argument(
        "--body-file",
        type=Path,
        help="Markdown PR description; updates existing PR if supplied",
    )
    stage = parser.add_mutually_exclusive_group()
    stage.add_argument(
        "--files", nargs="+", help="Exact repository-relative files to stage"
    )
    stage.add_argument(
        "--all", action="store_true", help="Explicitly include ALL nonignored changes"
    )
    parser.add_argument("--draft", action="store_true", help="Create a draft PR")
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Show scope and checks; no checks or mutations",
    )
    args = parser.parse_args()
    root = Path(git(Path(args.repo).resolve(), "rev-parse", "--show-toplevel"))
    if (args.sync_source or args.push_sync) and args.sync is None:
        fail("--sync-source and --push-sync require --sync.")
    if args.init and args.sync is not None:
        fail("--init cannot be combined with --sync.")
    if args.init and args.promote:
        fail("--init cannot be combined with --promote.")
    if args.init:
        initialize(root, args.base)
        return
    config = json.loads((root / CONFIG).read_text())
    if args.base:
        config["base"] = args.base
    validate_config(config)
    if args.sync is not None:
        sync_branches(root, config, args)
        return
    if args.promote:
        promote(root, config, args)
        return
    base, remote = config["base"], config["remote"]
    branch = git(root, "branch", "--show-current")
    if not branch:
        fail("Detached HEAD. Switch to a named task branch first.")
    if git(root, "diff", "--name-only", "--diff-filter=U"):
        fail("Unresolved conflicts. Resolve them before delivery.")
    for operation in (
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "rebase-merge",
        "rebase-apply",
    ):
        if Path(git(root, "rev-parse", "--git-path", operation)).is_absolute():
            operation_path = Path(git(root, "rev-parse", "--git-path", operation))
        else:
            operation_path = root / git(root, "rev-parse", "--git-path", operation)
        if operation_path.exists():
            fail(
                "A Git merge/rebase/cherry-pick/revert is in progress. Finish or abort it first."
            )
    if args.plan:
        print(
            json.dumps(
                {
                    "repository": str(root),
                    "branch": branch,
                    "base": base,
                    "checks": config["checks"],
                    "scope": args.files
                    or (
                        "ALL nonignored changes" if args.all else "already staged files"
                    ),
                    "start": args.start,
                },
                indent=2,
            )
        )
        print(git(root, "status", "--short"))
        return
    if args.start:
        if git(root, "status", "--porcelain"):
            fail(
                "--start requires a clean worktree. Preserve existing work before starting."
            )
        name = "codex/" + args.start
        run(["git", "check-ref-format", "--branch", name], root)
        run(["git", "fetch", remote, base], root)
        run(["git", "switch", "-c", name, f"{remote}/{base}"], root)
        return
    if branch in PROTECTED or branch == base:
        fail(
            "Delivery requires a task branch. Use --start feature-task BEFORE editing."
        )
    if not args.message or not args.message.strip() or args.message.startswith("-"):
        fail("Supply --message with a concrete description of the change.")
    body = args.body_file.resolve().read_text() if args.body_file else None
    run(["gh", "auth", "status"], root)
    selected = None
    if args.files:
        selected = set(args.files)
        for name in selected:
            path = Path(name)
            if path.is_absolute() or ".." in path.parts or name.startswith("-"):
                fail("--files accepts exact repository-relative paths only.")
            if (root / path).is_dir():
                fail("Use exact file paths, not directories, with --files.")
        staged = set(
            filter(None, git(root, "diff", "--cached", "--name-only", "-z").split("\0"))
        )
        if staged - selected:
            fail(
                "Other files are already staged. Review/unstage them or include them explicitly."
            )
    if args.all:
        run(["git", "add", "--all"], root)
    elif selected:
        run(["git", "add", "--", *sorted(selected)], root)
    guard_staged(root)
    run(["git", "diff", "--cached", "--check"], root)
    if git(root, "diff", "--name-only") or git(
        root, "ls-files", "--others", "--exclude-standard"
    ):
        fail(
            "Unselected or unstaged changes remain. Use an isolated worktree or explicitly select the intended files."
        )
    index_before_checks = git(root, "write-tree")
    for command in config["checks"]:
        run(command, root)
    if (
        git(root, "diff", "--name-only")
        or git(root, "ls-files", "--others", "--exclude-standard")
        or git(root, "write-tree") != index_before_checks
    ):
        fail(
            "Checks changed nonignored files or the index. Review changes and rerun delivery."
        )
    changed = bool(git(root, "diff", "--cached", "--name-only"))
    if changed:
        run(["git", "diff", "--cached", "--stat"], root)
        run(["git", "commit", "-m", args.message], root)
    elif git(root, "status", "--porcelain"):
        fail("Changes are unstaged. Select --files or deliberately use --all.")
    if git(root, "status", "--porcelain"):
        fail(
            "Uncommitted changes remain after commit/checks. Review them before publishing."
        )
    run(["git", "fetch", remote, base], root)
    if not git(root, "log", "--format=%H", f"{remote}/{base}..HEAD"):
        fail("No commits ahead of the base; nothing to publish.")
    run(["git", "push", "-u", remote, branch], root)
    github_repository = github_repo(root, remote)
    prs = json.loads(
        run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                github_repository,
                "--state",
                "open",
                "--base",
                base,
                "--head",
                branch,
                "--json",
                "number,url",
            ],
            root,
            capture=True,
        ).stdout
    )
    if prs:
        url = prs[0]["url"]
        if body is not None:
            run(
                [
                    "gh",
                    "pr",
                    "edit",
                    str(prs[0]["number"]),
                    "--repo",
                    github_repository,
                    "--title",
                    args.title or args.message,
                    "--body",
                    body,
                ],
                root,
            )
        print("Updated branch for existing PR: " + url)
    else:
        if body is None:
            commits = git(root, "log", "--format=- %s", f"{remote}/{base}..HEAD")
            checks = "\n".join(
                "- Passed: `" + " ".join(command) + "`" for command in config["checks"]
            )
            body = f"{args.title or args.message}\n\nChanges:\n{commits}\n\nValidation:\n{checks}\n\nGenerated by git-deliver.py. CI must pass before merge."
        argv = [
            "gh",
            "pr",
            "create",
            "--repo",
            github_repository,
            "--base",
            base,
            "--head",
            branch,
            "--title",
            args.title or args.message,
            "--body",
            body,
        ]
        if args.draft:
            argv.append("--draft")
        run(argv, root)
    print(
        "Delivery complete. The PR is not merged; inspect CI and reviews before approval."
    )


if __name__ == "__main__":
    try:
        main()
    except (
        ValueError,
        OSError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"Stopped: {error}", file=sys.stderr)
        sys.exit(1)
