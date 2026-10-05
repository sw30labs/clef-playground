# Clef playground

Run Cloudflare Clef locally on Apple Silicon with a browser playground and a
SystemOne-compatible decision endpoint. Supply text or JSON plus typed questions
and inspect the probability of each allowed answer.

This project uses the community [27B 8-bit MLX conversion](https://huggingface.co/mlx-community/clef-8bit)
of [Cloudflare Clef](https://huggingface.co/Cloudflare/clef). The custom decision
head is preserved in BF16. It is a decision model; ordinary chat generation does
not run this head.

## Requirements

- Apple Silicon Mac and Python 3.12.
- The model publisher recommends at least 48 GB of unified memory for this variant.
- About 30 GB for the model, plus space for the Python environment.
- Internet access during installation and model download. Inference runs offline.

## Setup

Clone this repository and create an isolated environment:

```sh
git clone https://github.com/sw30labs/clef-playground.git
cd clef-playground
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python download_model.py
./start.command
```

Alternatively, if you use `uv`, replace the two environment/install commands with:

```sh
uv venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.lock.txt
```

The launcher opens **http://127.0.0.1:8766** after the model loads. Keep the terminal
open while testing and press Control-C to stop. On later runs, double-click
`start.command` or run it again. To select another port, use `./start.command --port 8767`.

The downloader fetches the exact revision in `model-manifest.json` and checks file
sizes. Interrupted downloads can be resumed by running it again. To check an
existing download without network access:

```sh
.venv/bin/python download_model.py --verify-only
```

## Try a decision

Choose an example in the browser, edit the state and question schema, and select
**Run decision**. The three question types are:

| Type | Output |
| --- | --- |
| `choice` | Named options, their probabilities, and the selected option |
| `noul` | Probability that a proposition is true |
| `score` | Ordered options and their probability-weighted average, indexed from zero |

The same server provides `GET /health` and `POST /v1/systemone`:

```sh
curl http://127.0.0.1:8766/v1/systemone \
  -H 'Content-Type: application/json' \
  -d '{"state":"Checkout fails for every customer.","questions":{"outage":{"type":"noul","instructions":"Is checkout unavailable?"}}}'
```

The playground accepts text and JSON only. It binds to localhost, loads one model,
and runs inference one request at a time. Inputs above 16,384 tokens are rejected
instead of truncated. Upstream Python support for images and video is outside the
tested scope of this playground.

## Smoke tests

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python smoke_test.py \
  --model model --output results/smoke-test.json
```

Three synthetic cases cover paid and overdue invoices and a complete checkout
outage, with nine expected decisions across all question types. Checks include
finite probabilities, normalization, answer expectations, and confidence/score
consistency. Reports record full responses, timings, memory, and model provenance.

On an M3 Ultra with 512 GB unified memory, all three cases passed. Inference took
2.7–4.2 seconds per case, with peak MLX memory of 30.3 GB. These are functional
smoke tests, not a general accuracy or performance benchmark. The local HTTP API
also passed a synthetic invoice check. Browser interaction was not visually
verified in the original setup session.

Model weights, caches, environments, and local reports are excluded from Git.

## License and attribution

Apache-2.0. The unchanged vendored MLX adapter and its upstream license are in
`vendor/`. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for provenance.
This project is not affiliated with Cloudflare or the MLX community.
