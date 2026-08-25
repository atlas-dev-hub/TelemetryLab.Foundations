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
<summary>Prefer your own machine to a Codespace?</summary>

Everything runs locally. You need Docker, Python 3.12+ and Node 22.15+.

```bash
git clone <this repository>
cd <this repository>
pip install -r producer/requirements.txt
(cd consumer && npm install)
alias lab='python .lab/lab.py'
lab
```

</details>
