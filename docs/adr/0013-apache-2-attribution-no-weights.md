# 0013. License the project Apache-2.0, keep third-party attribution explicit, and distribute no weights

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

The project combines original code with an upstream adapter and points at a community conversion of a Cloudflare model.

## Decision

License the repo under Apache-2.0 (copyright SW3.0 Labs). Keep the upstream license unchanged in `vendor/LICENSE`, describe provenance in `THIRD_PARTY_NOTICES.md`, state that weights are not distributed and are fetched with their own model card and license, and state in the README and UI footer that the project is not affiliated with Cloudflare or the MLX community.

## Consequences

### Positive

- Clear provenance and license terms for reuse.
- No redistribution of model weights from this repo.

### Negative

- The upstream license file's copyright line reads 'Alibaba Cloud', which a reader may not expect for a Cloudflare model (A-011).
- The model's own license terms are only reachable after download.

## Alternatives considered

- None recorded.

## Evidence

- `LICENSE`
- `vendor/LICENSE`
- `THIRD_PARTY_NOTICES.md`
- `README.md` (License and attribution)
- `playground.html` footer
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
