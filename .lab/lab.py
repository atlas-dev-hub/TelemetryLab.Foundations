#!/usr/bin/env python3
"""
The `lab` command.

The problem this solves: a learner opens a Codespace and is looking at a file
tree. Nothing on screen says which module they are on, what they are supposed to
do, or whether what they just did worked. The README says it, but only if they
find it, open it, and scroll to the right place.

So the terminal answers instead, because the terminal is where they already are:

    lab            where you are and what to do next
    lab check      run the real validator here, before you push
    lab submit     branch, commit, push, open the pull request

`lab check` is the important one. Without it the feedback loop is: push, wait
two minutes for CI, read a comment, fix, push again. With it the loop is a few
seconds and runs the *identical* validator, so a local pass means a CI pass.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import socket
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.join(ROOT, ".lab")
PROGRESS = os.path.join(LAB, "progress.json")
VALIDATE = os.path.join(LAB, "validate.py")

STACK = [("Stream API", 13579), ("Kafka", 9092), ("Key Generator", 15379)]
UP = "docker compose up -d --wait kafka stream-api key-generator"

BOLD, DIM, GREEN, RED, YELLOW, OFF = "\033[1m", "\033[2m", "\033[32m", "\033[31m", "\033[33m", "\033[0m"
if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    BOLD = DIM = GREEN = RED = YELLOW = OFF = ""


def titles() -> dict[int, str]:
    """Module names, taken from the validator so the two cannot drift apart."""
    spec = importlib.util.spec_from_file_location("_lab_validate", VALIDATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {n: t for n, (t, _) in mod.MODULES.items()}


def state() -> dict:
    with open(PROGRESS, encoding="utf-8") as f:
        return json.load(f)


def port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", port)) == 0


def stack_down() -> list[str]:
    return [name for name, port in STACK if not port_open(port)]


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()


def handle() -> str:
    """The learner's GitHub handle, which is the owner of their own repository."""
    if os.environ.get("GITHUB_USER"):
        return os.environ["GITHUB_USER"]
    url = git("remote", "get-url", "origin")
    if "github.com" in url:
        tail = url.split("github.com")[-1].lstrip(":/")
        if "/" in tail:
            return tail.split("/")[0]
    return ""


# --- commands ---------------------------------------------------------------


def cmd_status(_args) -> int:
    st = state()
    module = st["module"]
    names = titles()
    total = len(names)
    done = set(st.get("completed", []))

    print()
    print(f"  {BOLD}ATLAS Telemetry Lab{OFF}")
    print()
    for n in sorted(names):
        if n in done:
            print(f"  {GREEN}[x]{OFF} {DIM}{n}. {names[n]}{OFF}")
        elif n == module:
            print(f"  {BOLD}[ ] {n}. {names[n]}   <- you are here{OFF}")
        else:
            print(f"  {DIM}[ ] {n}. {names[n]}{OFF}")
    print()

    if module > total:
        print(f"  {GREEN}All {total} modules complete.{OFF} See README.md.")
        print()
        return 0

    print(f"  {BOLD}What to do now{OFF}")
    print()
    print(f"    1. Read the instructions:  {BOLD}README.md{OFF}  {DIM}(module {module} is at the top){OFF}")
    print("    2. Make the change it asks for")
    print(f"    3. Check your work:        {BOLD}lab check{OFF}")
    print(f"    4. Submit it:              {BOLD}lab submit{OFF}")
    print()

    missing = stack_down()
    if missing:
        print(f"  {YELLOW}The telemetry stack is not running{OFF} ({', '.join(missing)}).")
        print(f"  Start it with:  {BOLD}{UP}{OFF}")
        print()
    return 0


def cmd_check(_args) -> int:
    st = state()
    module = st["module"]
    names = titles()

    if module not in names:
        print("Nothing left to check - every module is complete.")
        return 0

    missing = stack_down()
    if missing:
        print()
        print(f"  {RED}The telemetry stack is not running.{OFF}")
        print(f"  Missing: {', '.join(missing)}")
        print()
        print("  Start it, wait for it to be healthy, then try again:")
        print()
        print(f"      {BOLD}{UP}{OFF}")
        print()
        return 1

    print(f"{DIM}Running the same validator the bot runs. This takes a minute.{OFF}\n")
    # Flush before handing the terminal to the child, or our banner lands
    # underneath its output.
    sys.stdout.flush()
    # The report contains em dashes. Without this, a Windows console encodes
    # them with the ANSI codepage and the learner reads mojibake.
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(
        [sys.executable, VALIDATE, str(module), "--handle", handle()], cwd=ROOT, env=env
    )
    print()
    if result.returncode == 0:
        print(f"  {GREEN}Module {module} passes.{OFF}  Submit it with:  {BOLD}lab submit{OFF}")
    else:
        # The validator's own report already says what to do. Do not say it
        # twice; just make it obvious at a glance which way it went.
        print(f"  {RED}Module {module} does not pass yet.{OFF}")
    print()
    return result.returncode


def cmd_submit(_args) -> int:
    st = state()
    module = st["module"]
    branch = f"module-{module}"

    if not git("status", "--porcelain") and git("rev-parse", "--abbrev-ref", "HEAD") == "main":
        print("Nothing to submit - you have not changed anything yet. See README.md.")
        return 1

    current = git("rev-parse", "--abbrev-ref", "HEAD")
    if current != branch:
        subprocess.run(["git", "checkout", "-B", branch], cwd=ROOT, check=True)

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
    if git("diff", "--cached", "--name-only"):
        subprocess.run(
            ["git", "commit", "-m", f"Module {module}"], cwd=ROOT, check=True
        )
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=ROOT, check=True)

    title = f"Module {module}"
    pr = subprocess.run(
        ["gh", "pr", "create", "--fill", "--base", "main", "--head", branch,
         "--title", title, "--body", f"Submitting module {module}."],
        cwd=ROOT, capture_output=True, text=True,
    )
    if pr.returncode == 0:
        print()
        print(f"  {GREEN}Pull request opened.{OFF} The bot is validating it now.")
        print(f"  {pr.stdout.strip()}")
        print()
        print(f"  {DIM}It comments on the pull request either way. On a pass it advances")
        print(f"  your README to the next module and merges.{OFF}")
        print()
        return 0

    # gh missing or not authenticated - the push worked, so say what is left.
    existing = "already exists" in (pr.stderr or "")
    if existing:
        print(f"\n  {GREEN}Pushed.{OFF} The pull request already open for `{branch}` will re-run.\n")
        return 0
    url = git("remote", "get-url", "origin").removesuffix(".git")
    print()
    print(f"  {GREEN}Pushed `{branch}`.{OFF}")
    print(f"  {YELLOW}Could not open the pull request for you{OFF} - open it here:")
    print(f"      {url}/compare/main...{branch}?expand=1")
    print(f"  {DIM}{(pr.stderr or '').strip().splitlines()[0] if pr.stderr else ''}{OFF}")
    print()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="lab", description="ATLAS Telemetry Lab")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status", help="where you are and what to do next")
    sub.add_parser("check", help="run the validator locally, before you push")
    sub.add_parser("submit", help="branch, commit, push, open the pull request")
    args = ap.parse_args()

    return {
        None: cmd_status,
        "status": cmd_status,
        "check": cmd_check,
        "submit": cmd_submit,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
