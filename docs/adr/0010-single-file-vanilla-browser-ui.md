# 0010. Ship the browser UI as one static HTML file with inline CSS and plain JavaScript

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

The playground needs a simple way to edit a state and a question schema and inspect per-option probabilities, served by the same local process.

## Decision

`playground.html` holds all markup, CSS and JavaScript with no build step, framework or external assets. It loads examples from `/examples`, posts to `/v1/systemone` on the same origin, renders results with `createElement` and `textContent` only, and shows the raw response. State text that looks like JSON is parsed before sending, mirroring the adapter's CLI behaviour.

## Consequences

### Positive

- No Node toolchain or CDN; works offline and passes the same-origin check in ADR 0006.
- Model output is never inserted as HTML, which avoids script injection from returned strings.

### Negative

- One dense file with minified-style CSS is harder to edit.
- No automated UI test; the README says browser interaction was not visually verified in the original session.

## Alternatives considered

- A front-end framework or separate static bundle (not mentioned).

## Evidence

- `playground.html`
- `playground.py` `index()` and `examples()`
- `README.md` (Smoke tests, last paragraph)
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
