# Architecture Decision Records

Retrospective ADRs for `clef-playground`, written on 2026-11-02 from the default branch `main` at `93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2`.
Each records a decision that the code and commit history already show. Where the reason is inferred rather than written down, the ADR says so and the inference is logged in [../assumptions.md](../assumptions.md).

Format: Title; Status; Context; Decision; Consequences (positive and negative); Alternatives considered; Evidence.

The repository has a single commit (2026-10-05), so every ADR shares the same commit evidence and decision date.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-local-clef-on-apple-silicon-mlx-8bit.md) | Run Cloudflare Clef locally on Apple Silicon through the community 8-bit MLX conversion | Accepted (retrospective, inferred 2026-11-02) |
| [0002](0002-vendor-upstream-adapter-unchanged.md) | Vendor the upstream Clef MLX adapter unchanged, pinned by revision and SHA-256 | Accepted (retrospective, inferred 2026-11-02) |
| [0003](0003-pinned-model-revision-size-manifest.md) | Fetch weights at setup from a pinned Hub revision into a repo-local folder and verify them against a size manifest | Accepted (retrospective, inferred 2026-11-02) |
| [0004](0004-offline-only-inference.md) | Run inference fully offline once installed | Accepted (retrospective, inferred 2026-11-02) |
| [0005](0005-own-fastapi-server-systemone-endpoint.md) | Serve the playground and a SystemOne-compatible endpoint from a small FastAPI app instead of the adapter's built-in server | Accepted (retrospective, inferred 2026-11-02) |
| [0006](0006-localhost-only-request-hardening.md) | Bind to localhost and harden the API against browser cross-origin and oversized requests | Accepted (retrospective, inferred 2026-11-02) |
| [0007](0007-text-json-only-validated-schema.md) | Accept text and JSON only, and validate the question schema before inference | Accepted (retrospective, inferred 2026-11-02) |
| [0008](0008-never-truncate-reject-over-limit.md) | Never truncate input; reject requests above 16,384 tokens | Accepted (retrospective, inferred 2026-11-02) |
| [0009](0009-single-model-serialised-main-thread-inference.md) | Load one model and run inference serially on the loading thread | Accepted (retrospective, inferred 2026-11-02) |
| [0010](0010-single-file-vanilla-browser-ui.md) | Ship the browser UI as one static HTML file with inline CSS and plain JavaScript | Accepted (retrospective, inferred 2026-11-02) |
| [0011](0011-exact-dependency-lock-python-312.md) | Pin every Python dependency exactly and support Python 3.12 with pip or uv | Accepted (retrospective, inferred 2026-11-02) |
| [0012](0012-synthetic-example-smoke-test.md) | Check the install with three synthetic cases and a JSON report, not a test framework or benchmark | Accepted (retrospective, inferred 2026-11-02) |
| [0013](0013-apache-2-attribution-no-weights.md) | License the project Apache-2.0, keep third-party attribution explicit, and distribute no weights | Accepted (retrospective, inferred 2026-11-02) |
| [0014](0014-double-click-macos-launcher.md) | Start the playground from a double-clickable macOS `start.command` on port 8766 | Accepted (retrospective, inferred 2026-11-02) |
