#!/usr/bin/env bash
#
# Reference solution for Module 4 (Python + confluent-kafka).
# A learner's version of this file does whatever their language needs.
set -euo pipefail
python -m pip install --quiet --disable-pip-version-check confluent-kafka
python .lab/reference-solutions/module4/main.py
