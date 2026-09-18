#!/usr/bin/env python3
"""
Report one anonymous grading result to the course authors.

Runs in the grading workflow, only if the learner opted in with `lab share on`.
It sends the module number, pass or fail, a random per-copy ID and the
template version. Never the username, repository name or any code.

This must never fail a grade. Every exception is caught, the exit code is
always 0, and the workflow step that runs it ignores the result anyway.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.dirname(os.path.abspath(__file__))
PROGRESS = os.path.join(LAB, "progress.json")
VERSION = os.path.join(LAB, "VERSION")

DEFAULT_ENDPOINT = "https://atlastelemetrylab.netlify.app/api/progress"
AUDIENCE = "atlas-telemetry-lab"
TIMEOUT = 10
MAX_HOPS = 3


class NoRedirect(urllib.request.HTTPRedirectHandler):
    # urllib turns a redirected POST into a GET. Refusing here makes a redirect
    # surface as an HTTPError so we can re-POST the same body ourselves.
    def redirect_request(self, *_args, **_kwargs):
        return None


def version() -> str:
    try:
        with open(VERSION, encoding="utf-8") as f:
            return f.read().strip() or "unknown"
    except OSError:
        return "unknown"


def oidc_token() -> str:
    url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
    req = urllib.request.Request(
        f"{url}&audience={AUDIENCE}",
        headers={"Authorization": f"bearer {os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']}"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)["value"]


def post(url: str, body: bytes, headers: dict) -> int:
    # Generated repos are frozen snapshots of whatever URL was current when
    # they were made, and the site will move domains. Follow a few hops.
    opener = urllib.request.build_opener(NoRedirect)
    for _ in range(MAX_HOPS + 1):
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with opener.open(req, timeout=TIMEOUT) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 307, 308) and e.headers.get("Location"):
                url = e.headers["Location"]
                continue
            raise
    raise RuntimeError("too many redirects")


def main() -> int:
    try:
        with open(PROGRESS, encoding="utf-8") as f:
            share = json.load(f).get("share") or {}
        if share.get("enabled") is not True:
            return 0

        module = int(os.environ["LAB_MODULE"])
        passed = os.environ.get("LAB_PASSED", "").lower() == "true"
        from advance import TOTAL
        ver = version()
        event = {
            "v": 1,
            "event": "module_result",
            "course": "foundations",
            "module": module,
            "passed": passed,
            "learner_id": share["id"],
            "template_version": ver,
            "run_id": os.environ.get("GITHUB_RUN_ID", ""),
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
            "total_modules": TOTAL,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {oidc_token()}",
            "User-Agent": f"telemetry-lab-report/{ver}",
        }
        status = post(os.environ.get("LAB_ENDPOINT") or DEFAULT_ENDPOINT,
                      json.dumps(event).encode("utf-8"), headers)
        if not 200 <= status < 300:
            raise RuntimeError(f"HTTP {status}")
        print(f"progress: reported module {module} {'pass' if passed else 'fail'}")
    except Exception as e:  # noqa: BLE001 - by design, see the docstring
        if isinstance(e, urllib.error.HTTPError):
            reason = f"HTTP {e.code}"
        elif isinstance(e, KeyError):
            reason = f"no {e.args[0]}"
        else:
            reason = str(e) or type(e).__name__
        print(f"progress: not reported ({reason})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
