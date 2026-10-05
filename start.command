#!/bin/zsh
set -e
cd -- "${0:A:h}"
if [[ ! -x .venv/bin/python ]]; then
  print "The local Python environment is missing. Complete setup first."
  read -r "reply?Press Return to close. "
  exit 1
fi
exec .venv/bin/python playground.py --open-browser "$@"
