#!/usr/bin/env bash
#
# Runs once, when the Codespace is created.
#
# Order matters here, and it is not the obvious one. The guidance — the `lab`
# command and the terminal greeting — is installed FIRST, before any of the slow
# work, because the learner can open a terminal the moment the Codespace appears
# and the slow work takes minutes. Installed last, `lab` is missing during
# exactly the window when someone is most likely to be looking for it.
set -euo pipefail
cd "$(dirname "$0")/.."
WORKSPACE="$PWD"
MARKER="$WORKSPACE/.lab/.setup-complete"
rm -f "$MARKER"

# --- guidance first, it costs a second ---------------------------------------

sudo tee /usr/local/bin/lab >/dev/null <<EOF
#!/usr/bin/env bash
exec python3 "$WORKSPACE/.lab/lab.py" "\$@"
EOF
sudo chmod +x /usr/local/bin/lab

# Every new terminal says where they are. The first one in a session gets the
# full picture; later ones get a single line, because fifteen lines of banner
# every time you open a split terminal is its own kind of unhelpful.
if ! grep -q "lab status" "$HOME/.bashrc" 2>/dev/null; then
  cat >>"$HOME/.bashrc" <<'EOF'

# --- ATLAS Telemetry Lab ---
if [ -x /usr/local/bin/lab ] && [ -z "${LAB_QUIET:-}" ]; then
  if [ ! -f /tmp/.lab-greeted ]; then
    touch /tmp/.lab-greeted
    lab status
  else
    printf '\033[2m  lab status  ·  lab check  ·  lab submit\033[0m\n'
  fi
fi
EOF
fi

# --- then the slow part ------------------------------------------------------

echo "Installing the producer's dependencies..."
pip install --quiet --disable-pip-version-check -r producer/requirements.txt

echo "Installing the reference consumer..."
(cd consumer && npm install --silent --no-audit --no-fund)

# Pull the images now, so that when Module 1 asks for `docker compose up` it
# starts in seconds rather than fetching ~400 MB while the learner watches a
# progress bar. They still run the command — that is the module — but the
# waiting happens here, before they are paying attention.
#
# `--progress quiet` matters: without it compose animates a spinner, and since
# this is running into a log file rather than a terminal, that arrives as
# thousands of lines of ANSI cursor-movement escapes.
echo "Pre-pulling the telemetry stack (this is the slow bit)..."
docker compose --progress quiet pull kafka stream-api key-generator ||
  echo "  (pull failed — 'docker compose up' will fetch them instead)"

touch "$MARKER"
echo
echo "Ready. Run 'lab' at any point to see where you are."
