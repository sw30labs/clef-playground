# 0004. Run inference fully offline once installed

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

The README promises that inference runs offline and the UI says all inference stays on the Mac. The Hugging Face and Transformers libraries can otherwise reach the network at import or load time, and the adapter's `load()` downloads a repo id when given one.

## Decision

`playground.py` sets `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` and `HF_HUB_DISABLE_TELEMETRY=1` before any model library is imported, and loads only from the local `model/` directory. The README's smoke-test command sets the same offline variables. Network access is limited to installation and `download_model.py`.

## Consequences

### Positive

- No request data or telemetry leaves the machine during use.
- Behaviour does not depend on Hub availability after setup.

### Negative

- Any missing tokenizer or config file fails at load rather than being fetched, which is intended but strict.
- `smoke_test.py` itself does not set the offline variables; it relies on the caller doing so as the README shows.

## Alternatives considered

- Allow online fallback for missing files (not taken).

## Evidence

- `playground.py` (environment block at the top)
- `README.md` (Requirements, Smoke tests)
- `playground.html` intro text
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
