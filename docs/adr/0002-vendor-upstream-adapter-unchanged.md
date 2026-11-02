# 0002. Vendor the upstream Clef MLX adapter unchanged, pinned by revision and SHA-256

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

Loading Clef needs model code for the joint head and the record encoding. That code ships with the model repo as `clef_mlx.py`, and the model files are only fetched at setup time.

## Decision

Copy `clef_mlx.py` from `mlx-community/clef-8bit` revision `ffcdb6132b3cc94e523860321dd9ed58bc1ee9a1` into `vendor/` without changes, record its source URL and SHA-256 in `THIRD_PARTY_NOTICES.md`, and keep the upstream Apache-2.0 license next to it byte-for-byte (`.gitattributes` disables text normalisation so its CRLF endings survive). Project code imports it by putting `vendor/` on `sys.path`. Upstream features the playground does not use (images, video, the adapter's own `serve` and `predict` commands) are left in place and blocked at the playground layer instead of being edited out.

## Consequences

### Positive

- The adapter is reviewable in the repo and does not change when the Hub copy changes.
- The recorded SHA-256 matches the tracked file (`852223c9...97d5`, checked during this review), so provenance can be re-verified.
- Keeping it unchanged keeps attribution and license compliance simple.

### Negative

- The adapter relies on mlx-vlm internals and warns when mlx-vlm or mlx-lm drift from the tested minor versions, so upgrades need re-testing.
- The same file is also downloaded into `model/` as part of the manifest, so two copies exist on disk; only the vendored one is imported.
- Unused code paths (media decoding, an HTTP server that fetches image URLs) remain in the tree.

## Alternatives considered

- Import the adapter from the downloaded `model/` folder (would make code depend on a downloaded artifact; not stated as considered).
- Edit or trim the adapter (rejected implicitly by the 'unchanged' wording in `THIRD_PARTY_NOTICES.md`).

## Evidence

- `vendor/clef_mlx.py`
- `vendor/LICENSE`
- `.gitattributes`
- `THIRD_PARTY_NOTICES.md`
- `playground.py` and `smoke_test.py` (`sys.path.insert(0, ... 'vendor')`)
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
