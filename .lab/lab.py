#!/usr/bin/env python3
"""
The `lab` command.

The problem this solves: a learner opens a Codespace and is looking at a file
tree. Nothing on screen says which module they are on, what they are supposed to
do, or whether what they just did worked. The README says it, but only if they
find it, open it, and scroll to the right place.

So the terminal answers instead, because the terminal is where they already are:

    lab            where you are and what to do next
    lab explain    why this stage works the way it does, with the real protobuf
    lab check      run the real validator here, before you push
    lab submit     push, open the pull request, wait for the verdict, move on
    lab share      opt in or out of anonymous progress reporting

`lab check` is the important one. Without it the feedback loop is: push, wait
two minutes for CI, read a comment, fix, push again. With it the loop is a few
seconds and runs the *identical* validator, so a local pass means a CI pass.

`lab explain` is the one that decides whether anybody leaves here able to build
something. The modules teach the commands; explain teaches the platform.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.join(ROOT, ".lab")
PROGRESS = os.path.join(LAB, "progress.json")
VALIDATE = os.path.join(LAB, "validate.py")
# Written by .devcontainer/post-create.sh when it finishes. `lab` is installed
# first and the image pull happens last, so there is a window of a few minutes
# where the command exists but the stack it talks about is not downloaded yet.
SETUP_DONE = os.path.join(LAB, ".setup-complete")
# Touched once the learner has been asked about progress sharing, so the
# question is never asked twice on this machine even if they never answered.
SHARE_ASKED = os.path.join(LAB, ".share-asked")
PRIVACY_URL = "https://atlastelemetrylab.netlify.app/privacy/"

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


def save_state(st: dict) -> None:
    # Same bytes advance.py writes, so the bot's commit and ours never differ
    # in whitespace alone.
    with open(PROGRESS, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2)
        f.write("\n")


def port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", port)) == 0


def setting_up() -> bool:
    """True while post-create is still working. Only meaningful in a container."""
    return os.path.isdir("/workspaces") and not os.path.exists(SETUP_DONE)


def stack_down() -> list[str]:
    return [name for name, port in STACK if not port_open(port)]


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()


REBASE_HINT = (
    "Your work could not be replayed on top of the latest `main`. The rebase\n"
    "  has been undone, so nothing is lost. Resolve it by hand with:\n"
    "      git fetch origin main && git rebase origin/main"
)

PUSH_HINT = (
    "Git could not authenticate. Inside a Codespace this normally just works —\n"
    "  if it does not, check you are in the integrated terminal rather than an\n"
    "  ssh session, since the credentials live in the login shell environment.\n"
    "  On your own machine, run `gh auth login` (or set up an SSH key) first."
)


def step(cmd: list[str], hint: str = "") -> bool:
    """Run a git step, and explain rather than traceback when it fails.

    A learner who sees a Python stack trace has been handed our problem, and
    nothing in it tells them what to do next.
    """
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode == 0:
        return True
    print()
    print(f"  {RED}`{' '.join(cmd)}` failed.{OFF}")
    detail = (r.stderr or r.stdout or "").strip()
    for line in detail.splitlines()[:4]:
        print(f"    {DIM}{line}{OFF}")
    if hint:
        print()
        print(f"  {hint}")
    print()
    return False


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


# --- progress sharing --------------------------------------------------------
#
# Off unless the learner says yes. When it is on, the grading workflow sends
# one anonymous event per run (see .lab/report.py). Nothing here can affect a
# grade: `lab` only ever writes a flag into progress.json.


def set_share(st: dict, enabled: bool) -> None:
    """Flip the flag, keeping the same random ID across on/off/on."""
    import uuid
    from datetime import date

    share = st.get("share") or {}
    st["share"] = {
        "enabled": enabled,
        "id": share.get("id") or str(uuid.uuid4()),
        "since": share.get("since") or date.today().isoformat(),
    }
    save_state(st)
    open(SHARE_ASKED, "w").close()


def share_prompt() -> None:
    """Ask once, at the first `lab submit`, and only when a person is there.

    Runs before `git add -A` so the answer travels in the same pull request the
    bot is about to grade. A non-tty (the bashrc hook, a pipe, CI) is never
    asked, and neither is anyone who has answered before on any machine.
    """
    if "share" in state() or os.path.exists(SHARE_ASKED):
        return
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        return

    print()
    print(f"  {BOLD}Share anonymous progress with the course authors? [y/N]{OFF}")
    print("    If you say yes, each graded pull request sends the module number,")
    print("    pass or fail, and a random ID for this copy of the course.")
    print("    The report contains no username, repository name or code.")
    print("    It tells us which module people get stuck on.")
    print(f"    Change it any time:  {BOLD}lab share off{OFF}   {DIM}(takes effect on your next submit){OFF}")
    print(f"    {DIM}Details: {PRIVACY_URL}{OFF}")
    print()
    try:
        answer = input("  > ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = ""
    print()

    st = state()
    if answer in ("y", "yes"):
        set_share(st, True)
        print(f"  {GREEN}Sharing on.{OFF} {DIM}Thank you. `lab share off` turns it off.{OFF}")
    else:
        # Recorded as a decision, not just a marker file, so a second machine
        # (or a rebuilt Codespace) does not ask again.
        st["share"] = {"enabled": False}
        save_state(st)
        open(SHARE_ASKED, "w").close()
        print(f"  {DIM}Sharing off. `lab share on` turns it on.{OFF}")
    print()


def cmd_share(args) -> int:
    mode = getattr(args, "mode", "status") or "status"
    st = state()
    share = st.get("share")

    if mode == "on":
        set_share(st, True)
        print(f"\n  {GREEN}Progress sharing on{OFF} from the next `lab submit`."
              f"  {DIM}lab share off{OFF} stops it.\n")
        return 0
    if mode == "off":
        set_share(st, False)
        print(f"\n  Progress sharing {BOLD}off{OFF} from the next `lab submit`."
              f"  {DIM}lab share on{OFF} resumes it.\n")
        return 0

    print()
    if share is None:
        print(f"  Progress sharing: {BOLD}off{OFF} {DIM}(not asked yet; `lab submit` asks once){OFF}")
    elif share.get("enabled") is True:
        print(f"  Progress sharing: {GREEN}on{OFF}  {DIM}·  lab share off{OFF}")
    else:
        print(f"  Progress sharing: {BOLD}off{OFF}  {DIM}·  lab share on{OFF}")
    print()
    print("  When on, each time the bot grades a pull request it sends the module")
    print("  number, pass or fail, and a random ID for this copy of the course.")
    print("  The report contains no username, repository name or code.")
    print(f"  {DIM}{PRIVACY_URL}{OFF}")
    print()
    return 0


# --- commands ---------------------------------------------------------------


def synced() -> bool:
    """Move onto main after the bot has merged a module.

    The bot advances README.md and .lab/progress.json, squash-merges into main
    and deletes the branch. The learner's checkout is still sitting on that
    branch with the old files, so `lab` would keep reporting the module they
    just finished, and the next module's work would start on the wrong branch.

    Uncommitted work is never touched: if the tree is dirty this reports and
    does nothing. The merge is --ff-only, so it cannot rewrite anything either.
    """
    subprocess.run(["git", "fetch", "--quiet", "--prune", "origin"],
                   cwd=ROOT, capture_output=True, text=True)
    behind = git("rev-list", "--count", "main..origin/main")
    if not behind or behind == "0":
        return False

    if git("status", "--porcelain"):
        print()
        print(f"  {YELLOW}Your module was merged, but you have uncommitted changes.{OFF}")
        print("  Commit or stash them, then run `lab` again to move on.")
        print()
        return False

    was = git("rev-parse", "--abbrev-ref", "HEAD")
    if was != "main":
        if not step(["git", "checkout", "main"]):
            return False
    if not step(["git", "merge", "--ff-only", "origin/main"]):
        return False

    # The branch was squash-merged, so `git branch -d` would refuse it - the
    # commits are not ancestors of main. It is gone from the remote, which is
    # the thing that actually tells us it is finished with.
    if was.startswith("module-") and not git("ls-remote", "--heads", "origin", was):
        subprocess.run(["git", "branch", "-D", was], cwd=ROOT, capture_output=True, text=True)

    print()
    print(f"  {GREEN}Merged.{OFF} Pulled the advance onto main"
          + (f" and cleaned up `{was}`." if was != "main" else "."))
    return True


def _render(body: str) -> None:
    """Markdown, lightly, for a terminal. Headings and bold only - anything more
    and it stops looking like the tool and starts looking like a web page."""
    import re
    # Emphasis is resolved over the whole body rather than line by line: a
    # **bold phrase** that wraps onto a second line would otherwise print its
    # asterisks literally, which is worse than not having bold at all.
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: BOLD + m.group(1) + OFF, body, flags=re.S)
    text = re.sub(r"(?<![*\w])\*([^*\n]+?)\*(?!\*)",
                  lambda m: DIM + m.group(1) + OFF, text)
    for line in text.rstrip().split("\n"):
        if line.startswith("## "):
            print(f"\n  {BOLD}{line[3:]}{OFF}")
            continue
        print("  " + line if line else "")


def cmd_explain(args) -> int:
    """The why behind the stage they are on, or any topic by name."""
    import explain as ex

    topics = ex.available()
    if not topics:
        print("No explanations are installed.")
        return 1

    name = getattr(args, "topic", None)
    if name in ("list", "topics"):
        name = None
        args.list = True

    if getattr(args, "list", False):
        print()
        print(f"  {BOLD}lab explain <topic>{OFF}")
        print()
        width = max(len(t) for t in topics)
        current = ex.for_module(state()["module"])
        for t, head in topics.items():
            mark = f"  {DIM}(module {head['module']}){OFF}" if head.get("module") else ""
            here = f"  {GREEN}<- you are here{OFF}" if t == current else ""
            print(f"    {BOLD}{t:<{width}}{OFF}  {head.get('title', '')}{mark}{here}")
        print()
        return 0

    if not name:
        name = ex.for_module(state()["module"])
        if not name:
            args.list = True
            return cmd_explain(args)

    if name not in topics:
        close = [t for t in topics if name in t or t in name]
        print(f"\n  {RED}No topic called `{name}`.{OFF}"
              + (f" Did you mean `{close[0]}`?" if close else ""))
        print(f"  {DIM}lab explain --list{OFF}\n")
        return 1

    head, body = ex._split(os.path.join(ex.TOPICS_DIR, name + ".md"))
    print()
    print(f"  {BOLD}{head.get('title', name)}{OFF}")
    if head.get("module"):
        print(f"  {DIM}module {head['module']}{OFF}")
    _render(body)

    # The definitions, pulled out of this repository's own .proto files by
    # message name. This is the part a learner cannot get from copying commands:
    # the actual contract, with the comments the protocol authors wrote.
    refs = (head.get("proto") or "").split()
    shown = False
    for ref in refs:
        got = ex.proto_excerpt(ref)
        if not got:
            continue
        text, where = got
        if not shown:
            print(f"\n  {BOLD}The definition{OFF}")
            shown = True
        print(f"\n  {DIM}{where}{OFF}")
        for line in text.split("\n"):
            print(f"    {DIM}{line}{OFF}" if line.strip().startswith("//") else f"    {line}")

    print(f"\n  {BOLD}Where to look next{OFF}\n")
    if head.get("code"):
        print(f"    in this repo   {head['code']}")
    for ref in refs:
        got = ex.proto_excerpt(ref)
        if got:
            print(f"    protobuf       {got[1]}")
            break
    if head.get("docs"):
        print(f"    documentation  {head['docs']}")
    if head.get("source"):
        print(f"    platform source {head['source']}")
    print()
    return 0


def cmd_status(_args) -> int:
    synced()
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

    share = st.get("share")
    if share is not None:
        if share.get("enabled") is True:
            print(f"  {DIM}Progress sharing: on  ·  lab share off{OFF}")
        else:
            print(f"  {DIM}Progress sharing: off  ·  lab share on{OFF}")
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
    print(f"    {DIM}Not sure why any of this works?  {OFF}{BOLD}lab explain{OFF}")
    print()

    if setting_up():
        print(f"  {YELLOW}Setup is still running.{OFF} It is downloading the telemetry stack —")
        print("  a few minutes on a fresh Codespace. Read the module meanwhile; run")
        print(f"  {BOLD}lab{OFF} again before you start step 1.")
        print()
        return 0

    missing = stack_down()
    if missing:
        print(f"  {YELLOW}The telemetry stack is not running{OFF} ({', '.join(missing)}).")
        print(f"  Start it with:  {BOLD}{UP}{OFF}")
        print()
    return 0


def cmd_check(_args) -> int:
    # Otherwise a stale progress.json re-validates the module you just passed.
    synced()
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


def wait_for_bot(branch: str, minutes: int = 8) -> str | None:
    """Block until the bot has ruled on the pull request.

    Validation takes about two minutes. Waiting here means the learner sees the
    verdict where they are working instead of going to find the pull request,
    and it is what lets `lab submit` hand them straight to the next module.
    """
    deadline = time.time() + minutes * 60
    print(f"  {DIM}Waiting for the bot. This usually takes about two minutes;")
    print(f"  Ctrl-C to stop watching - it keeps running either way.{OFF}")
    last = ""
    try:
        while time.time() < deadline:
            r = subprocess.run(
                ["gh", "pr", "view", branch, "--json", "state", "-q", ".state"],
                cwd=ROOT, capture_output=True, text=True)
            st = (r.stdout or "").strip()
            if st in ("MERGED", "CLOSED"):
                return st
            if st and st != last:
                last = st
            time.sleep(10)
    except KeyboardInterrupt:
        print(f"\n  {DIM}Stopped watching. Run `lab` when it finishes.{OFF}\n")
        return None
    except FileNotFoundError:
        return None
    print(f"\n  {YELLOW}Still running after {minutes} minutes.{OFF} Run `lab` later to pick it up.\n")
    return None


def bot_verdict(branch: str) -> str:
    r = subprocess.run(
        ["gh", "pr", "view", branch, "--json", "comments",
         "-q", ".comments[-1].body"], cwd=ROOT, capture_output=True, text=True)
    return (r.stdout or "").strip()


def cmd_submit(args) -> int:
    st = state()
    module = st["module"]
    branch = f"module-{module}"

    if not git("status", "--porcelain") and git("rev-parse", "--abbrev-ref", "HEAD") == "main":
        print("Nothing to submit - you have not changed anything yet. See README.md.")
        return 1

    # After the nothing-to-submit check: answering writes progress.json, which
    # would otherwise turn an empty submit into a pull request of just that.
    share_prompt()

    current = git("rev-parse", "--abbrev-ref", "HEAD")
    if current != branch:
        if not step(["git", "checkout", "-B", branch]):
            return 1

    if not step(["git", "add", "-A"]):
        return 1
    if git("diff", "--cached", "--name-only"):
        if not step(["git", "commit", "-m", f"Module {module}"]):
            return 1

    # Rebase onto current main before pushing.
    #
    # A repository generated from the template gets a README rewrite pushed to
    # main by the welcome workflow moments later. Open the Codespace fast
    # enough and you cloned before that; branch from there and your first pull
    # request cannot be merged. Rebasing here means the learner never sees it.
    if step(["git", "fetch", "origin", "main"]):
        if not step(["git", "rebase", "origin/main"], hint=REBASE_HINT):
            subprocess.run(["git", "rebase", "--abort"], cwd=ROOT,
                           capture_output=True, text=True)
            return 1

    if not step(["git", "push", "--force-with-lease", "-u", "origin", branch],
                hint=PUSH_HINT):
        return 1

    title = f"Module {module}"
    try:
        pr = subprocess.run(
            ["gh", "pr", "create", "--base", "main", "--head", branch,
             "--title", title, "--body", f"Submitting module {module}."],
            cwd=ROOT, capture_output=True, text=True,
        )
    except FileNotFoundError:
        # No GitHub CLI here. The push already worked, so the only thing left
        # is a link — not an error.
        pr = None

    if pr is not None and pr.returncode == 0:
        print()
        print(f"  {GREEN}Pull request opened.{OFF}  {pr.stdout.strip()}")
        print()
        if getattr(args, "no_wait", False):
            print(f"  {DIM}Not waiting. Run `lab` once it has merged.{OFF}\n")
            return 0

        outcome = wait_for_bot(branch)
        verdict = bot_verdict(branch) if outcome else ""
        if verdict:
            print()
            for line in verdict.splitlines():
                print("  " + line)
        if outcome == "MERGED":
            synced()
            print()
            return cmd_status(args)
        if outcome == "CLOSED":
            print(f"\n  {RED}The pull request was closed without merging.{OFF}\n")
            return 1
        return 0

    # gh missing or not authenticated — the push worked, so say what is left.
    err = (pr.stderr or "") if pr is not None else ""
    if "already exists" in err:
        print(f"\n  {GREEN}Pushed.{OFF} The pull request already open for `{branch}` will re-run.\n")
        return 0
    url = git("remote", "get-url", "origin").removesuffix(".git")
    print()
    print(f"  {GREEN}Pushed `{branch}`.{OFF}")
    print(f"  {YELLOW}Open the pull request here:{OFF}")
    print(f"      {url}/compare/main...{branch}?expand=1")
    if err.strip():
        print(f"  {DIM}{err.strip().splitlines()[0]}{OFF}")
    print()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="lab", description="ATLAS Telemetry Lab")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status", help="where you are and what to do next")
    sub.add_parser("check", help="run the validator locally, before you push")
    p_ex = sub.add_parser("explain", help="the why behind this stage, or any topic")
    p_ex.add_argument("topic", nargs="?", help="topic name; omit for the one you are on")
    p_ex.add_argument("--list", action="store_true", help="list the topics")
    p_submit = sub.add_parser("submit", help="branch, commit, push, open the pull request")
    p_submit.add_argument("--no-wait", action="store_true",
                          help="do not wait for the bot's verdict")
    p_share = sub.add_parser("share", help="opt in or out of anonymous progress reporting")
    p_share.add_argument("mode", nargs="?", choices=["on", "off", "status"], default="status",
                         help="on, off, or status (the default)")
    args = ap.parse_args()

    return {
        None: cmd_status,
        "status": cmd_status,
        "check": cmd_check,
        "explain": cmd_explain,
        "submit": cmd_submit,
        "share": cmd_share,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
