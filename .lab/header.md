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
   | `lab check` | Runs the real validator here, in seconds. Nothing is pushed. |
   | `lab submit` | Branches, commits, pushes and opens the pull request. |

`lab check` runs the *identical* code the bot runs, so a pass here is a pass
there. Use it as often as you like — it is free and it is local.

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
