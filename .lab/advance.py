#!/usr/bin/env python3
"""
Advance the learner to the next module.

Rewrites README.md from the module templates and bumps .lab/progress.json.
The workflow commits the result, which is why the learner's repo carries a
visible, honest history of their progress rather than a hidden score.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.join(ROOT, ".lab")
MODULES = os.path.join(LAB, "modules")
PROGRESS = os.path.join(LAB, "progress.json")
README = os.path.join(ROOT, "README.md")

TOTAL = 4


def load() -> dict:
    with open(PROGRESS, encoding="utf-8") as f:
        return json.load(f)


def save(state: dict) -> None:
    with open(PROGRESS, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def render(state: dict) -> str:
    module = state["module"]
    name = "done" if module > TOTAL else f"{module:02d}"
    with open(os.path.join(MODULES, f"{name}.md"), encoding="utf-8") as f:
        body = f.read()

    done = state.get("completed", [])
    ticks = " ".join(
        ("[x]" if i in done else "[ ]") + f" {i}" for i in range(1, TOTAL + 1)
    )
    header = (
        "# ATLAS Telemetry Lab\n\n"
        "> Learn to build on an open, real-time telemetry platform — by building on it.\n\n"
        f"**Progress:** {ticks}\n\n"
        "---\n\n"
    )
    return header + body


def main() -> int:
    state = load()
    completed = state["module"]

    if completed not in state["completed"]:
        state["completed"].append(completed)
    if len(sys.argv) > 1:
        state.setdefault("runs", {})[str(completed)] = sys.argv[1]
    state["module"] = completed + 1

    save(state)
    with open(README, "w", encoding="utf-8") as f:
        f.write(render(state))

    nxt = state["module"]
    print(f"advanced: module {completed} complete -> " + ("finished" if nxt > TOTAL else f"module {nxt}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
