# MVP findings

What building and running this actually proved, and what it broke on.

**Verdict: the model works.** A learner takes a template, does a module on a
branch, opens a PR in their own repo, and a bot validates it, comments, advances
the README and merges. Proven end to end, twice, in a real repository.

Test run: [`federicadonald/lab-learner-test`](https://github.com/federicadonald/lab-learner-test)
— two modules, two PRs, both merged by the bot.

---

## The feasibility question, answered

**The fear:** new repositories default to `default_workflow_permissions: "read"`.
If that capped what a workflow can request, the bot could not comment, commit or
merge, and every learner would need to change a setting before starting.

**It doesn't.** A `permissions:` block in the workflow granting `contents: write`
and `pull-requests: write` works in a fresh template-generated repository with
the default `read` setting. Verified: the bot commented, committed and merged
with no setup step at all.

That was the single biggest risk to the design, and it is closed.

## Cost, measured

| | |
|---|---|
| Validation run | **~2 minutes** (1.7 and 2.3 min observed) |
| Cost to the learner | **Zero** — Actions is free on public repositories |
| Cost to us | **Zero** — it runs entirely in their repo |

A nine-module course is roughly 20 minutes of compute per learner, all of it on
GitHub's free tier.

## Five things it broke on

Every one of these would have hit the first real learner.

### 1. The zstd codec needed a C++ compiler

`@kafkajs/zstd` — the obvious choice, and what the working lab used — pulls in
`cppzst`, a native module built with `node-gyp`. It compiles on some machines
and not others, and it **failed outright on the GitHub runner**.

For a lab this is disqualifying: `npm install` becomes a coin flip for someone
whose actual goal is telemetry, not toolchains.

Node has had zstd in `node:zlib` since 22.15, so
[`consumer/src/zstd.js`](consumer/src/zstd.js) is now twenty lines with no
native dependency. The whole tree is pure JavaScript.

### 2. kafkajs wants a factory, not a codec

Registering `CompressionCodecs[ZSTD] = codecObject` fails with `codec is not a
function` — but only at decode time, long after connecting and reporting topic
offsets successfully. It reads like a broker problem. It is a missing pair of
parentheses.

### 3. The protobuf pin was wrong, and only CI could tell us

The generated stubs are gencode 6.31.1; `requirements.txt` pinned runtime
5.29.1. Protobuf enforces matching major versions, so it failed at import.

It never appeared locally because the development machine had an unpinned 6.x
installed — the pin had never actually been exercised until a clean runner used
it. A textbook case for validating in a clean environment rather than a
developer's.

### 4. The validator looked for sessions in the wrong place

`GetCurrentSessions` returns *live* sessions. A well-behaved producer closes its
session when it finishes — so by validation time there was nothing to find, and
the validator reported "no session reached the Stream API" for a session that
had worked perfectly.

Now the producer emits a machine-readable `LAB_SESSION=` line (printed only
after a successful `CreateSession` round-trip), and Kafka topic offsets confirm
the data independently.

### 5. The bot raced itself

The bot commits the advance to the PR branch, then merges the PR. That push
makes the head SHA GitHub knows about stale, and `gh pr merge` fails with *"Head
branch is out of date"*.

Fixed by merging via the API with the explicit SHA just pushed, plus a short
retry for propagation lag.

---

## What the evidence trail looks like

After finishing, the learner's own `.lab/progress.json` holds:

```json
{
  "module": 3,
  "completed": [1, 2],
  "runs": {
    "1": "https://github.com/.../actions/runs/32744454392",
    "2": "https://github.com/.../actions/runs/32744766524"
  }
}
```

Those URLs are public, permanent, and checkable by anyone — including by a
registry bot verifying a completion claim, and by a hiring manager who wants to
see the work rather than a badge.

## Still to prove

- **Codespaces.** The MVP was validated through Actions. The one-click browser
  path is configured but untested.
- **The registry.** No central completion record yet — that is design §3.
- **Someone who is not us.** Everything here was driven by the person who wrote
  it. The gate that matters is five external people finishing Foundation.

## Known rough edges

- A re-run on a branch *after* the bot has advanced it will validate the next
  module against the current PR. Harmless in the happy path (the merge follows
  immediately), but worth making robust.
- Module content is duplicated between `.lab/modules/` and the rendered README.
  Fine at two modules; wants a check at nine.
