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
