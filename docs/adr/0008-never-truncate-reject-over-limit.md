# 0008. Never truncate input; reject requests above 16,384 tokens

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

The adapter mirrors the reference encoder, which by default trims the state to fit the context window. Silently trimming the state can change a decision without the caller knowing.

## Decision

Always call `model.systemone(..., max_length=16384, truncate=False)`. Requests that do not fit raise `ContextTooLong` and return HTTP 413 with a message that nothing was truncated. Clients cannot turn truncation back on: `validate()` drops any `truncate` field. `/health` advertises `max_context_tokens: 16384` and `truncate: false`, and the UI and README repeat the rule. The smoke test also runs with `truncate=False`.

## Consequences

### Positive

- Every decision is made on the full input the caller sent.
- The limit is visible to clients through `/health`.

### Negative

- Long states fail instead of degrading; callers must shorten input themselves.
- Behaviour differs from the adapter's and the reference encoder's default.

## Alternatives considered

- Keep upstream truncation (default in the adapter; overridden here).
- Make truncation a per-request option, as the adapter's server does (explicitly blocked).

## Evidence

- `playground.py` (`MAX_LENGTH`, `systemone()`, `validate()` comment, `health()`)
- `vendor/clef_mlx.py` `encode_record()` and `_cmd_serve()`
- `smoke_test.py` (`truncate=False`)
- `README.md`
- `playground.html` help text
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
