# 0003. Fetch weights at setup from a pinned Hub revision into a repo-local folder and verify them against a size manifest

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

The model is roughly 30 GB and cannot live in Git. Setup must be repeatable, resumable, and must not silently pick up a newer upload.

## Decision

`model-manifest.json` lists the Hub repo, an exact revision SHA and every file with its byte size. `download_model.py` calls `snapshot_download` with that revision and an allow-list of exactly those files, into `model/`, with `HF_HOME` defaulting to a repo-local `.hf-cache/`. Both the downloader (`--verify-only`), the server at startup and the smoke test refuse to run if any file is missing or has the wrong size. Weights, caches and environments are git-ignored.

## Consequences

### Positive

- Reproducible: every install resolves the same revision and file set.
- Interrupted downloads resume by re-running the script; offline re-verification is possible.
- Startup fails fast with a clear message instead of loading a partial model.

### Negative

- Verification is by size only, not by hash, so same-size corruption or substitution would pass the local check (A-005).
- A repo-local cache means a second copy of the weights if the user already has them in a global Hugging Face cache.

## Alternatives considered

- Commit weights with Git LFS (not mentioned).
- Track the latest revision (rejected implicitly by pinning).
- Verify SHA-256 per file (not done; see A-005).

## Evidence

- `model-manifest.json`
- `download_model.py`
- `playground.py` `lifespan()`
- `smoke_test.py` provenance checks
- `.gitignore` (`model/`, `.hf-cache/`, `*.safetensors`)
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
