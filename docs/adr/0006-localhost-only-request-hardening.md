# 0006. Bind to localhost and harden the API against browser cross-origin and oversized requests

## Status

Accepted (retrospective, inferred 2026-11-02)

## Context

A local model server on a fixed port can be reached by any web page the user opens, through cross-site requests or DNS rebinding, and a large body could tie up the single model.

## Decision

Bind uvicorn to `127.0.0.1`. Add `TrustedHostMiddleware` allowing only `localhost` and `127.0.0.1` Host headers. On `POST /v1/systemone`, reject any request that carries an `Origin` header other than the playground's own `http://127.0.0.1:<port>` or `http://localhost:<port>` (403); requests without an `Origin`, such as curl, are allowed. Stream the body and stop at 256 KiB (413). Serve the page with `Cache-Control: no-store` and `X-Content-Type-Options: nosniff`, and ignore any client-supplied model name. The threat model behind these checks is not written down; it is inferred (A-003).

## Consequences

### Positive

- Other origins in the browser cannot drive the model, and a rebinding hostname fails the Host check.
- Memory use per request is bounded before JSON parsing.

### Negative

- Not reachable from other machines on the LAN, by design; remote use needs a tunnel or code change.
- Non-browser local processes are not authenticated; anything running as the user can call the API.

## Alternatives considered

- The adapter's server, which binds to 127.0.0.1 but has no Host or Origin checks and allows 64 MB bodies (present in the tree, not used).
- Token authentication (not mentioned).

## Evidence

- `playground.py` (`TrustedHostMiddleware`, `systemone()` origin check, `MAX_BODY`, `index()` headers, `uvicorn.run(host='127.0.0.1')`)
- `README.md` ('It binds to localhost')
- Commit 93c8a2333e3c6ca03bec77f5a1c703a0e4f634c2 (2026-10-05, the repository's only commit)
