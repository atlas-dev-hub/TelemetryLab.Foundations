#!/usr/bin/env bash
#
# Runs once, when the Codespace is created.
#
# Two jobs. Install things, and make sure the learner cannot end up staring at a
# file tree with no idea what to do — which is what happens by default, because
# a fresh Codespace tells you nothing about the repository you just opened.
set -euo pipefail
cd "$(dirname "$0")/.."
WORKSPACE="$PWD"

echo "Installing the producer's dependencies..."
pip install --quiet --disable-pip-version-check -r producer/requirements.txt

echo "Installing the reference consumer..."
(cd consumer && npm install --silent --no-audit --no-fund)

# Pull the images now, so that when Module 1 asks for `docker compose up` it
# starts in seconds rather than fetching ~400 MB while the learner watches a
# progress bar. They still run the command — that is the module — but the
# waiting happens here, before they are paying attention.
echo "Pre-pulling the telemetry stack..."
docker compose pull --quiet kafka stream-api key-generator ||
  echo "  (pull failed — 'docker compose up' will fetch them instead)"

# The `lab` command, on PATH.
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

echo
echo "Ready. Open a terminal and run 'lab' at any point to see where you are."
