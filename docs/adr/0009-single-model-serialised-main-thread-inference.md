# 0009. Load one model and run inference serially on the loading thread

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

MLX evaluation is tied to the thread and device it runs on, and the machine has one GPU. The comments say MLX must not move into a worker pool.

## Decision

Load the model once in the FastAPI lifespan, keep it in `app.state`, and guard inference with an `asyncio.Lock`. Call the synchronous `model.systemone` directly inside the async handler so it stays on the event-loop thread that loaded the model. Run uvicorn with `workers=1`. The only background thread is the helper that waits for `/health` and opens the browser; it never touches MLX. Whether the single-thread rule came from an observed failure is not recorded (A-004).

## Consequences

### Positive

- Predictable memory use and no cross-thread MLX errors.
- Requests are answered one at a time, matching the README.

### Negative

- While a decision runs, the event loop is blocked, so `/health`, `/examples` and the page itself wait too.
- No concurrency; throughput is one request at a time.

## Alternatives considered

- Run inference in a thread pool with `run_in_executor` (warned against in the code comment).
- Multiple workers, each loading the 30 GB model (not considered viable on one machine; inferred).

## Evidence

- `playground.py` (`lifespan()`, `app.state.lock`, comments on lines 36 and 134, `open_when_ready()` docstring, `workers=1`)
- `vendor/clef_mlx.py` `_cmd_serve()` ('one GPU: run requests one at a time')
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
