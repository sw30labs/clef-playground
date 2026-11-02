# 0005. Serve the playground and a SystemOne-compatible endpoint from a small FastAPI app instead of the adapter's built-in server

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

The vendored adapter already ships a `serve` command (a `ThreadingHTTPServer` on `POST /v1/systemone`). The playground also needs to serve an HTML page and example cases, and the project wanted stricter request handling than the adapter's defaults.

## Decision

`playground.py` is a FastAPI app run by uvicorn with one worker. It exposes `GET /` (the HTML page), `GET /health`, `GET /examples` and `POST /v1/systemone`, keeps the SystemOne request and response shape, adds `usage.latency_ms`, and disables the OpenAPI and docs routes. The adapter is used only as a library (`clef_mlx.load`, `model.systemone`). Why FastAPI rather than extending the adapter's server is inferred (A-002).

## Consequences

### Positive

- One process serves both the UI and an API that other SystemOne clients can call (A-008 on compatibility).
- Validation, limits and security headers live in project code without editing the vendored file (ADR 0002).

### Negative

- Adds FastAPI, Starlette and uvicorn to the dependency set.
- Two server implementations now exist in the tree (the adapter's unused one and this one).

## Alternatives considered

- Use `clef_mlx.py serve` directly (available but not used).
- Standard-library `http.server` like the adapter (not stated as considered).

## Evidence

- `playground.py`
- `vendor/clef_mlx.py` `_cmd_serve()`
- `README.md` (Try a decision)
- `requirements.lock.txt` (fastapi, starlette, uvicorn)
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
