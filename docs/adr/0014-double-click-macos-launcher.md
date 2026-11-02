# 0014. Start the playground from a double-clickable macOS `start.command` on port 8766

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

Day-to-day use should not need a terminal command once setup is done.

## Decision

`start.command` is a zsh script that changes to its own folder, stops with a message if `.venv` is missing, and execs `playground.py --open-browser` with any extra arguments. The server defaults to port 8766 (overridable with `--port`), and `--open-browser` polls `/health` for up to about ten minutes and opens the browser once the expected model answers. Why 8766 was chosen is not recorded (A-012).

## Consequences

### Positive

- Double-click start from Finder; the browser opens only when the model is ready.
- The health check confirms the expected model before opening, so another service on the same port is not opened by mistake.

### Negative

- macOS and zsh only.
- If the port is busy, the user has to pass `--port` themselves.

## Alternatives considered

- Running `python playground.py` by hand (still possible).

## Evidence

- `start.command`
- `playground.py` (`--port` default, `open_when_ready()`)
- `README.md` (Setup)
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
