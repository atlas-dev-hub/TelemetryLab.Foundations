#!/usr/bin/env python3
"""
`lab explain` — the why behind each stage.

A learner who only follows the modules ends up able to run this lab and unable
to build anything with the platform afterwards. The commands are the easy part;
what is worth carrying away is why a session is a first-class thing, why a
channel is more than a name, and which of these mistakes fail silently.

Each topic lives in .lab/explain/<topic>.md and declares the protobuf messages
it is about. The excerpts are pulled out of the repository's own .proto files at
run time, by message name rather than line number, so the explanation cannot
drift from the definitions it is describing — and the learner is reading the
real contract, not a paraphrase of it.
"""

from __future__ import annotations

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOPICS_DIR = os.path.join(HERE, "explain")
PROTO_DIR = os.path.join(ROOT, "consumer", "proto", "ma", "streaming")

PROTOS = {
    "open_data": os.path.join(PROTO_DIR, "open_data", "v1", "open_data.proto"),
    "api": os.path.join(PROTO_DIR, "api", "v1", "api.proto"),
    "key_generator": os.path.join(PROTO_DIR, "key_generator", "v1", "key_generator.proto"),
}


def available() -> dict[str, dict]:
    """Every topic, keyed by name, with its header fields."""
    out = {}
    if not os.path.isdir(TOPICS_DIR):
        return out
    for name in sorted(os.listdir(TOPICS_DIR)):
        if not name.endswith(".md"):
            continue
        head, _ = _split(os.path.join(TOPICS_DIR, name))
        out[name[:-3]] = head
    return out


def for_module(n: int) -> str | None:
    for topic, head in available().items():
        if head.get("module") and head["module"].strip() == str(n):
            return topic
    return None


def _split(path: str) -> tuple[dict, str]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if "\n---\n" not in text:
        return {}, text
    header, body = text.split("\n---\n", 1)
    fields = {}
    for line in header.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return fields, body.lstrip("\n")


def proto_excerpt(ref: str) -> tuple[str, str] | None:
    """Pull a message out of a .proto by name.

    Resolved at run time rather than stored as a line range, because a line
    range is wrong the first time anyone edits the file above it.
    """
    if ":" not in ref:
        return None
    file_key, message = ref.split(":", 1)
    path = PROTOS.get(file_key)
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")

    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^(message|enum|service)\s+{re.escape(message)}\b", line):
            start = i
            break
    if start is None:
        return None
    # Walk back over the leading comment - it is usually the best sentence
    # anyone has written about the message.
    while start > 0 and lines[start - 1].lstrip().startswith("//"):
        start -= 1
    depth = 0
    for j in range(start, len(lines)):
        depth += lines[j].count("{") - lines[j].count("}")
        if depth == 0 and j > start:
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            return "\n".join(lines[start:j + 1]), f"{rel}:{start + 1}"
    return None
