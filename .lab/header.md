# ATLAS Telemetry Lab

> Learn to build on an open, real-time telemetry platform — by building on it.

This is **your** copy. Work here; nothing you do touches anyone else's.

## Do this now

1. **Open a Codespace.** `Code` → `Codespaces` → `Create codespace on main`.
   First build takes a few minutes — it is installing Docker, Python and Node so
   that you do not have to. Later opens are quick.
2. **Wait for the terminal.** When it appears it will print where you are and
   what to do. You can ask it again at any time:

   ```bash
   lab
   ```
3. **Follow the module below.** Then:

   | Command | What it does |
   |---|---|
   | `lab explain` | Why this stage works the way it does, with the real protobuf. |
   | `lab check` | Runs the real validator here, in seconds. Nothing is pushed. |
   | `lab submit` | Pushes, opens the pull request, and waits for the verdict. |
   | `lab share` | Opt in or out of anonymous progress reporting. Off by default. |

`lab check` runs the *identical* code the bot runs, so a pass here is a pass
there. Use it as often as you like — it is free and it is local.

`lab submit` stays with you: it waits for the bot, prints what it found, and
moves you onto the next module once it merges. You never need to
`git checkout main && git pull` — press Ctrl-C if you would rather not wait, and
run `lab` later to pick up where it got to.

<details>
<summary>`lab` or `docker` not found?</summary>

Then your Codespace did not build, and GitHub quietly gave you a **recovery
container** instead — a bare Linux box with your files mounted and none of the
tools. It looks like a working Codespace, which is what makes it confusing.

Check with:

```bash
ls /workspaces/.codespaces/.persistedshare/RECOVERY-REASON-FILE
```

If that file exists, rebuild: **Command Palette** (`F1`) →
**Codespaces: Rebuild Container**. If it fails again, the reason is in
`/workspaces/.codespaces/.persistedshare/creation.log` — please open an issue
and paste the first `ERROR` line from it.

</details>

<details>
<summary>Prefer your own machine to a Codespace?</summary>

Everything runs locally. You need Docker, Python 3.12+ and Node 22.15+.

```bash
# your copy, not the template
git clone https://github.com/<you>/<your-repo>.git
cd <your-repo>
pip install -r producer/requirements.txt
(cd consumer && npm install)
alias lab='python .lab/lab.py'
lab
```

</details>

## Sharing your progress (optional, off by default)

This collects nothing unless you turn it on. The first time you run `lab
submit`, it asks once whether to share anonymous progress with the course
authors — say nothing, or say no, and nothing is ever sent.

If you opt in, each time the bot grades a pull request it sends the module
number, pass or fail, and a random ID for this copy of the course. Never your
username, your repository name, or your code — you can read exactly what it
sends in [`.lab/report.py`](.lab/report.py). Nothing about it can affect your
grade.

```bash
lab share on       # start sharing
lab share off      # stop  (takes effect on your next submit)
lab share status   # what it is set to now
```

Details: <https://atlastelemetrylab.netlify.app/privacy/>
