# ATLAS Telemetry Lab

> Learn to build on an open, real-time telemetry platform — by building on it.

## Start here

**Do not clone this repository, and do not fork it.**

1. Click **`Use this template` → `Create a new repository`** at the top of this page.
   Name it whatever you like — `telemetry-lab` is fine.
2. In *your* new repository: **`Code` → `Codespaces` → `Create codespace on main`**.
3. Wait for it to build, then follow the module below.

You need your own copy because you will be opening pull requests against it, and
a bot will be committing your progress back to it. A fork would not work: GitHub
disables Actions in forks by default, and a fork's pull requests default to
targeting *this* repository rather than yours.

<details>
<summary>Prefer your own machine?</summary>

Everything runs locally with Docker and no Codespace. You still want your own
repository from the template, so the validator can run and record your progress.

```bash
gh repo create my-telemetry-lab --private --template <this-repo>
cd my-telemetry-lab
pip install -r producer/requirements.txt
(cd consumer && npm install)
docker compose up -d --wait kafka stream-api key-generator
```

You will need Docker, Python 3.12+, and Node 22.15+.

</details>

---

**Progress:** [ ] 1 [ ] 2 [ ] 3 [ ] 4

---

## Module 1 — Make it yours

**Goal:** get a real telemetry pipeline running, and understand what a *session* is.

### Run it

```bash
docker compose up -d --wait kafka stream-api key-generator
cd producer && pip install -r requirements.txt
python produce.py --laps 1
```

A synthetic GT3 drives a lap of a fictional circuit at 60 Hz. Eleven channels
stream through the ATLAS Stream API into Kafka.

Nothing here needs a licence, a simulator, or any hardware.

### Your task

Open [`producer/produce.py`](producer/produce.py) and find `LAB_HANDLE` near the
top. Set it to your GitHub handle.

That is all — but notice *where* it ends up. `LAB_HANDLE` becomes part of the
**session identifier**, which is created before a single sample is sent and
travels with every packet after it.

That is what a session is: not an anonymous window of time, but a named thing
with a start, an end, and a configuration that belongs to it. It is the first of
the ideas a bare Kafka topic has no concept of.

### Submit it

```bash
git checkout -b module-1
git commit -am "Module 1: set my handle"
git push -u origin module-1
```

Then open a pull request against `main` **in your own repository**. A bot will
run the whole pipeline, check the session carries your handle, and tell you what
happened.

<details>
<summary>What is actually running?</summary>

| Service | Port | Role |
|---|---|---|
| `kafka` | 9092 | The broker. Holds the telemetry. |
| `stream-api` | 13579 | Producers talk gRPC to this. It never talks to ATLAS. |
| `key-generator` | 15379 | Unique ids for sessions and configuration. |

Producers do **not** write to Kafka directly. The Stream API is where a stream
of numbers becomes telemetry — it registers the session, holds the configuration
describing each channel, and allocates the data-format ids a consumer needs to
decode a packet. Write straight to a topic and the bytes land, but nothing can
read them.

</details>
