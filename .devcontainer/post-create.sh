#!/usr/bin/env bash
#
# Runs once, when the Codespace is created.
#
# Installs dependencies and pulls the stack's images, so that when Module 1 asks
# for `docker compose up` it starts in seconds rather than pulling ~400 MB while
# the learner watches a progress bar. They still run the command - that is the
# module - but the waiting happens here, before they are paying attention.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Installing the producer's dependencies..."
pip install --quiet --disable-pip-version-check -r producer/requirements.txt

echo "Installing the reference consumer..."
(cd consumer && npm install --silent --no-audit --no-fund)

echo "Pre-pulling the telemetry stack..."
docker compose pull --quiet kafka stream-api key-generator || \
  echo "  (pull failed - 'docker compose up' will fetch them instead)"

cat <<'BANNER'

  ATLAS Telemetry Lab is ready.

  Start here:  README.md
  Then:        docker compose up -d --wait kafka stream-api key-generator

BANNER
