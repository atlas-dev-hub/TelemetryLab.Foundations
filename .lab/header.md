<p align="center"><img src=".github/readme/banner.svg" alt="ATLAS Telemetry Lab. A lap trace drawn from real telemetry, coloured by speed." width="100%"></p>

This is your copy. Work here; nothing you do touches anyone else's.

## Do this now

1. Open a Codespace. `Code` → `Codespaces` → `Create codespace on main`. The
   first build takes a few minutes while it installs Docker, Python and Node.
   Later opens are quick.
2. Wait for the terminal. It runs `lab` on first open and prints where you are
   and what to do. Run it again at any time:

   ```bash
   lab
   ```
3. Follow the module below. Then:

   | Command | What it does |
   |---|---|
   | `lab` | Where you are and what to do next |
   | `lab explain` | Why this module works the way it does, with the real protobuf |
   | `lab check` | Runs the validator here, in seconds. Nothing is pushed |
   | `lab submit` | Pushes, opens the pull request and waits for the verdict |
   | `lab share` | Turns anonymous progress reporting on or off. Off by default |

`lab check` runs the same checks as the bot. If it passes here, it passes in
CI. Run it as often as you like.

`lab submit` waits for the bot, prints what it found, and moves you to the next
module once the pull request merges. You never need to
`git checkout main && git pull`. Press Ctrl-C if you would rather not wait, and
run `lab` later to catch up.

<details>
<summary>`lab` or `docker` not found?</summary>

Your Codespace did not build, and GitHub gave you a recovery container instead.
That is a bare Linux box with your files mounted and none of the tools. It
looks like a working Codespace.

Check with:

```bash
ls /workspaces/.codespaces/.persistedshare/RECOVERY-REASON-FILE
```

If that file exists, open the Command Palette (`F1`) and run
`Codespaces: Rebuild Container`. If it fails again, the reason is in
`/workspaces/.codespaces/.persistedshare/creation.log`. Open an issue and paste
the first `ERROR` line from it.

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

The course sends no data unless you opt in. The first time you run
`lab submit`, it asks whether to share anonymous progress with the course
authors. Answer no, or ignore the prompt, and it sends nothing.

If you opt in, each time the bot grades a pull request it sends the module
number, pass or fail, the course name and template version, and a random ID for
this copy. The report contains no username, repository name, or code.
[`.lab/report.py`](.lab/report.py) builds it in your own Actions and posts it
to Google Analytics. It has no effect on your grade.

```bash
lab share on       # start sharing
lab share off      # stop  (takes effect on your next submit)
lab share status   # what it is set to now
```

Details: <https://atlastelemetrylab.netlify.app/privacy/>
