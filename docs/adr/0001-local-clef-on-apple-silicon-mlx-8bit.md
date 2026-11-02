# 0001. Run Cloudflare Clef locally on Apple Silicon through the community 8-bit MLX conversion

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

Cloudflare Clef is a 27B decision model whose custom joint schema head returns probabilities over typed answers instead of generated text. The project's goal, per the README, is to try that model on a Mac with a browser playground and a SystemOne-compatible endpoint, with inference staying on the machine.

## Decision

Use the `mlx-community/clef-8bit` conversion: the backbone quantised to 8-bit, the joint head kept in BF16, loaded through the MLX adapter `clef_mlx.py`. Target Apple Silicon and Python 3.12 only. Why the 8-bit variant was picked over BF16 or the 4-bit Flash variants is not written down; see A-001.

## Consequences

### Positive

- No PyTorch or CUDA dependency; the adapter is torch-free.
- About 30 GB of weights and a reported peak of 30.3 GB MLX memory fit comfortably on the development Mac (README, unverified by this review).

### Negative

- Apple Silicon only. The README cites the publisher's 48 GB unified-memory recommendation, which excludes smaller Macs.
- 8-bit quantisation of the backbone may shift probabilities relative to the upstream BF16 model; no accuracy comparison is in the repo.

## Alternatives considered

- Upstream BF16 `Cloudflare/clef` under PyTorch (implied by the README's links; not stated as considered).
- A smaller quantisation such as the 4-bit Flash conversion that the adapter docstring uses as its example (not stated as considered).
- A hosted API (not mentioned).

## Evidence

- `README.md` (intro, Requirements)
- `model-manifest.json` (`repo_id`, `revision`)
- `THIRD_PARTY_NOTICES.md`
- `vendor/clef_mlx.py` docstring and `load()`
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
