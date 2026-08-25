# ATLAS Telemetry Lab

> Learn to build on an open, real-time telemetry platform — by building on it.

Four modules. A real broker, a real streaming API, a synthetic race car, and a
bot that checks your work and advances you when it passes. No licence, no
hardware, no simulator, and nothing to install.

## Start

**Do not clone this repository, and do not fork it.**

### 1. Make your own copy

Click **`Use this template` → `Create a new repository`** at the top of this
page. Name it whatever you like.

You need your own copy because you will be opening pull requests against it and
a bot will be committing your progress back to it. A fork would not work:
GitHub disables Actions in forks by default, and a fork's pull requests default
to targeting *this* repository rather than yours.

### 2. Open a Codespace on **your** repository

`Code` → `Codespaces` → `Create codespace on main`.

The first build takes a few minutes while it installs Docker, Python and Node.
When the terminal appears it tells you exactly where you are and what to do.

### 3. Run `lab`

Everything after that is driven from three commands, and the terminal reminds
you of them:

| Command | What it does |
|---|---|
| `lab` | Where you are and what to do next |
| `lab check` | Runs the real validator locally, in seconds |
| `lab submit` | Branches, commits, pushes, opens the pull request |

---

> **Already in your own copy and still seeing this page?** The welcome step did
> not run. Nothing is broken — open the Codespace and run `lab`, which will tell
> you where you are. To restore the guided README, run the **welcome** workflow
> from the `Actions` tab.

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
