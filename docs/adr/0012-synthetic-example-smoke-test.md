# 0012. Check the install with three synthetic cases and a JSON report, not a test framework or benchmark

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

The project needs a quick way to tell whether a local install produces sane SystemOne answers, without claiming accuracy.

## Decision

`smoke_test.py` loads the model, runs every JSON file in `examples/` (two invoices and one checkout outage, nine expected answers covering all three question types), and checks answer fields and types, finite probabilities in [0, 1], probabilities summing to 1 within a rounding tolerance, confidence matching the top probability, score matching the probability-weighted mean, and the expected top option or boolean. It writes a JSON report after every step with timings, peak MLX memory, package versions and the model manifest, and passes only if exactly three cases pass. The same example files feed the UI's example picker. No pytest suite or CI exists.

## Consequences

### Positive

- One set of examples serves both the UI and the check.
- Reports are inspectable even after a crash, since they are saved incrementally and non-finite numbers are stringified.

### Negative

- The pass rule is hard-coded to three cases, so adding a fourth example makes the run fail until the script is updated (A-010).
- Needs the full model and about 30 GB of memory, so it cannot run in ordinary CI; nothing runs automatically.
- Reports go to the git-ignored `results/`, so the README's timing and memory figures have no tracked artifact (A-007).

## Alternatives considered

- pytest unit tests with a mocked model (not present).
- An accuracy or throughput benchmark (explicitly ruled out in the docstring and README).

## Evidence

- `smoke_test.py`
- `examples/*.json`
- `playground.py` `examples()`
- `README.md` (Smoke tests)
- `.gitignore` (`results/`)
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
