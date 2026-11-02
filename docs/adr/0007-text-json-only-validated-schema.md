# 0007. Accept text and JSON only, and validate the question schema before inference

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

Upstream Clef and the adapter accept images and video. The README says those paths are outside the tested scope of this playground. Malformed schemas would otherwise surface as model or encoding errors.

## Decision

`validate()` rejects any request with `images`, `videos` or `media_kwargs`, requires `state`, requires 1 to 32 questions as an object, allows only the types `noul`, `choice` and `score`, requires 1 to 64 options for `choice` (object) and `score` (list), and allows optional `noul` criteria only as an object. It returns a fresh request containing only `model`, `state` and `questions`, dropping transport extras such as `truncate`. The 32 and 64 limits are not explained in the repo (A-009).

## Consequences

### Positive

- Clear 400 errors in the UI instead of stack traces.
- The untested media paths in the vendored adapter cannot be reached from the playground.

### Negative

- Users who want multimodal Clef must use the adapter directly.
- The limits are project choices, not upstream ones, and may reject requests that upstream SystemOne accepts.

## Alternatives considered

- Expose media through the playground (deliberately excluded per README).

## Evidence

- `playground.py` `validate()`
- `README.md` (text and JSON only; media outside tested scope)
- `playground.html` (help text)
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
