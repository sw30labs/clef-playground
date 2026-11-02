# 0011. Pin every Python dependency exactly and support Python 3.12 with pip or uv

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

The adapter depends on mlx-vlm internals that change between minor releases and states the versions it was tested with.

## Decision

`requirements.lock.txt` pins 57 packages to exact versions, including mlx 0.32.3, mlx-lm 0.32.0 and mlx-vlm 0.7.4, matching the adapter's tested versions. Setup creates a project `.venv` with Python 3.12 via `venv` or `uv`. There is no `pyproject.toml` and the lock has no hashes.

## Consequences

### Positive

- Installs match the tested environment, so the adapter's version warning should not fire.
- Either pip or uv works with the same file.

### Negative

- The lock pulls in packages the playground does not use directly, such as mlx-audio, opencv-python and sounddevice, presumably through mlx-vlm (A-006).
- Without hashes, the lock pins versions but not artifacts.
- Upgrades are manual and need re-running the smoke test.

## Alternatives considered

- A `pyproject.toml` with version ranges (not used).
- A hash-checked lock (`--require-hashes`) (not used).

## Evidence

- `requirements.lock.txt`
- `README.md` (Setup)
- `vendor/clef_mlx.py` (`TESTED_VERSIONS` comment)
- `.gitignore` (`.venv/`, `.uv-cache/`)
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
