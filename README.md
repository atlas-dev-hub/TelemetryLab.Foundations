# ATLAS Telemetry Lab

> Learn to build on an open, real-time telemetry platform — by building on it.

Four modules. A real broker, a real streaming API, a synthetic race car, and a
bot that checks your work and advances you when it passes. No licence, no
hardware, no simulator, and nothing to install.

## Start

**Do not clone this repository, and do not fork it.**

### 1. Make your own copy

Click **`Use this template` → `Create a new repository`** at the top of this
page (`mat-docs/TelemetryLab.Foundations`). Name it whatever you like.

You need your own copy because you will be opening pull requests against it and
a bot will be committing your progress back to it. A fork would not work:
GitHub disables Actions in forks by default, and a fork's pull requests default
to targeting *this* repository rather than yours.

### 2. Open a Codespace on **your** repository

`Code` → `Codespaces` → `Create codespace on main`.

The first build takes a few minutes while it installs Docker, Python and Node.
When the terminal appears it tells you exactly where you are and what to do.

### 3. Run `lab`

Everything after that is four commands, and the terminal reminds you of them:

| Command | What it does |
|---|---|
| `lab` | Where you are and what to do next |
| `lab explain` | Why this stage works the way it does, with the real protobuf |
| `lab check` | Runs the real validator locally, in seconds |
| `lab submit` | Branches, pushes, opens the pull request, waits for the verdict |
| `lab share` | Opt in or out of anonymous progress reporting |

`lab check` runs the identical code the bot runs, so a pass locally is a pass in
CI. `lab submit` then waits for the bot, prints its comment where you are
working, and moves you onto the next module once it merges — no `git pull`
needed.

---

> **Already in your own copy and still seeing this page?** The welcome step did
> not run. Nothing is broken — open the Codespace and run `lab`, which will tell
> you where you are. To restore the guided README, run the **welcome** workflow
> from the `Actions` tab.

## Sharing your progress (optional, off by default)

The course collects nothing unless you turn it on. The first time you run
`lab submit`, the tool asks once whether to share anonymous progress with the
course authors — say nothing, or say no, and nothing is ever sent.

If you opt in, then each time the bot grades a pull request **in your own
repository** it sends:

- the module number, and whether it passed or failed;
- the course name and template version;
- a random ID generated for your copy (not derived from anything about you).

It never sends your GitHub username, your repository name, or any of your code.
It runs entirely from your own GitHub Actions, so you can read exactly what it
sends in [`.lab/report.py`](.lab/report.py) — we host nothing and store nothing
of our own; the event goes to Google Analytics and that is the only place it
exists. None of it can affect your grade.

Change your mind at any time (it takes effect on your next submit):

```bash
lab share on       # start sharing
lab share off      # stop
lab share status   # what it is set to now
```

Full details, including what the site itself collects, are on the
[privacy page](https://atlastelemetrylab.netlify.app/privacy/).

## What the modules teach

The point is not "how to run Kafka". It is the things a bare topic and a
time-series database have no concept of, and which you would otherwise rebuild
by hand on every project.

| Module | What you do | What it is really about |
|---|---|---|
| 1 | Make it yours | **Sessions** — telemetry is not an anonymous window of time |
| 2 | Add a channel | **Parameter definitions** — identity, units, range, rate, in-band |
| 3 | Fix the broken producer | **Contiguous time** — a failure that reports success |
| 4 | Write your first consumer | Reading a stream you were never told the shape of |

## Understanding it, not just passing it

Every module has a `lab explain` topic behind it, and there are eight in total —
sessions, parameters, timestamps, packets, configuration, streams, the Stream
API and consumers.

Each one shows the **real protobuf definitions**, read out of this repository's
own `.proto` files at run time, and each ends with how to apply the idea to
systems of your own. The protocol details in them are checked against the
[Stream API](https://github.com/Software-Products/MA.DataPlatforms.StreamApi)
and [Protocol](https://github.com/Software-Products/MA.DataPlatforms.Protocol)
source, not written from memory.

```bash
lab explain            # the topic behind the module you are on
lab explain --list     # all eight
```

## What is running

| Service | Port | Role |
|---|---|---|
| `kafka` | 9092 | The broker. Holds the telemetry. |
| `stream-api` | 13579 | Producers talk gRPC to this. |
| `key-generator` | 15379 | Unique ids for sessions and configuration. |

Roughly 440 MiB at idle — comfortably inside the smallest Codespace, and well
inside the free tier for the length of the course.

## Cost

Nothing, to you or to us. Actions runs in your repository; on a public
repository that is free. Codespaces draws on your own free allowance (120
core-hours a month on a Free account, 180 on Pro, and students get Pro through
the GitHub Education pack). The whole course is well under one hour of compute.
