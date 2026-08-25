# Why this file exists.
#
# `mcr.microsoft.com/devcontainers/python` ships an apt source for Yarn's Debian
# repository. Yarn's repository signing subkeys expired on 2026-01-23, so
# `apt-get update` inside that image now fails with:
#
#     W: GPG error: https://dl.yarnpkg.com/debian stable InRelease:
#        NO_PUBKEY 62D54FD4003F6525
#
# Every dev container Feature that runs `apt-get update` during install then
# fails with exit 100 — for us that is docker-in-docker — and the whole
# container build fails. Codespaces does not surface that as an error: it
# quietly hands the learner a *recovery container* running Alpine with no
# Docker, no Node, and the repository mounted. The README then tells them to run
# `docker compose up`, and the command does not exist.
#
# We hit exactly that. See devcontainers/images#1797.
#
# Removing the source is the fix the upstream issue recommends and costs us
# nothing: this lab does not use Yarn. Features install on top of this image, so
# by the time docker-in-docker runs `apt-get update`, the broken source is gone.
#
# When upstream ships a fixed image this file can go away — but it is harmless
# to keep, and a silent recovery container is an expensive thing to debug twice.

FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

RUN find /etc/apt -name '*.list' -o -name '*.sources' \
      | xargs -r grep -l 'dl\.yarnpkg\.com' 2>/dev/null \
      | xargs -r rm -f \
  && apt-get update \
  && rm -rf /var/lib/apt/lists/*
