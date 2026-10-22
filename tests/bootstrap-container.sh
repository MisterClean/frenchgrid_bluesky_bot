#!/usr/bin/env bash
# Exercise a real root bootstrap with a restrictive umask and a separate user.
set -euo pipefail
commit=$(git rev-parse HEAD)
git archive HEAD | docker run --rm -i -e COMMIT="$commit" python:3.12-slim-bookworm bash -c '
  set -euo pipefail
  umask 077
  release=/opt/frenchgrid-bot/releases/$COMMIT
  mkdir -p "$release"
  tar -x -C "$release"
  printf "BOOTSTRAP_TEST=placeholder\n" > /etc/frenchgrid-bot.env
  # No service is started in the container; only staging is under test.
  printf "#!/bin/sh\nexit 0\n" > /usr/local/bin/systemctl
  chmod 0755 /usr/local/bin/systemctl
  bash "$release/deploy/install-service" "$COMMIT"
  runuser -u frenchgrid-bot -- env PYTHONDONTWRITEBYTECODE=1 "$release/.venv/bin/python" -c "import atproto, httpx, cryptography"
  runuser -u frenchgrid-bot -- test ! -w "$release/src/main.py"
  runuser -u frenchgrid-bot -- test ! -r /etc/frenchgrid-bot.env
  test "$(stat -c %a /var/lib/frenchgrid-bot)" = 700
'
