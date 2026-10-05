"""Local, text-only Clef playground. Run with this folder's .venv Python."""
from __future__ import annotations

import argparse
import asyncio
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

# Set before importing model libraries. All inference assets must already be local.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

HERE = Path(__file__).resolve().parent
MODEL_NAME = "mlx-community/clef-8bit"
MAX_BODY = 256 * 1024
MAX_LENGTH = 16384
sys.path.insert(0, str(HERE / "vendor"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load and infer on the same main thread. Do not move MLX into a worker pool.
    import clef_mlx

    manifest = json.loads((HERE / "model-manifest.json").read_text())
    for item in manifest["files"]:
        path = HERE / "model" / item["name"]
        if not path.is_file() or path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"Model download is incomplete: {item['name']}. Finish setup before starting.")
    print("Loading local Clef 8-bit model…", flush=True)
    app.state.model = clef_mlx.load(HERE / "model")
    app.state.lock = asyncio.Lock()
    app.state.context_error = clef_mlx.ContextTooLong
    print("Clef is ready. Press Control-C to stop.", flush=True)
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])


def error(message: str, status: int = 400) -> JSONResponse:
    return JSONResponse({"error": {"message": message}}, status_code=status)


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(
        (HERE / "playground.html").read_text(),
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME, "offline": True, "text_only": True,
            "max_context_tokens": MAX_LENGTH, "truncate": False}


@app.get("/examples")
async def examples():
    result = []
    for path in sorted((HERE / "examples").glob("*.json")):
        try:
            item = json.loads(path.read_text())
            request = item.get("request", item)
            if isinstance(request, dict) and "state" in request and "questions" in request:
                result.append({"name": item.get("title", item.get("name", path.stem.replace("_", " "))),
                               "state": request["state"], "questions": request["questions"]})
        except (OSError, ValueError, AttributeError):
            continue
    return result


def validate(payload):
    if not isinstance(payload, dict):
        raise ValueError("Send a JSON object containing state and questions.")
    if payload.get("images") or payload.get("videos") or payload.get("media_kwargs"):
        raise ValueError("This playground accepts text and JSON only; media is not supported.")
    if "state" not in payload or payload["state"] is None:
        raise ValueError("State is required.")
    questions = payload.get("questions")
    if not isinstance(questions, dict) or not 1 <= len(questions) <= 32:
        raise ValueError("Provide between 1 and 32 questions in a JSON object.")
    for key, question in questions.items():
        if not key or not isinstance(question, dict):
            raise ValueError("Every question needs a nonempty ID and a JSON object.")
        kind = question.get("type")
        criteria = question.get("criteria")
        if kind not in {"noul", "choice", "score"}:
            raise ValueError(f"{key}: type must be noul, choice, or score.")
        if kind == "choice" and (not isinstance(criteria, dict) or not 1 <= len(criteria) <= 64):
            raise ValueError(f"{key}: choice criteria must be an object with 1–64 options.")
        if kind == "score" and (not isinstance(criteria, list) or not 1 <= len(criteria) <= 64):
            raise ValueError(f"{key}: score criteria must be a list of 1–64 descriptions.")
        if kind == "noul" and criteria is not None and not isinstance(criteria, dict):
            raise ValueError(f"{key}: optional noul criteria must be an object.")
    # Ignore transport extras; never allow a request to select a model or enable truncation.
    return {"model": MODEL_NAME, "state": payload["state"], "questions": questions}


@app.post("/v1/systemone")
async def systemone(request: Request):
    origin = request.headers.get("origin")
    if origin and origin not in {f"http://127.0.0.1:{request.url.port}",
                                  f"http://localhost:{request.url.port}"}:
        return error("Use the local playground to submit browser requests.", 403)
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > MAX_BODY:
            return error("Request is larger than the 256 KiB limit.", 413)
    try:
        payload = validate(json.loads(data))
    except (ValueError, TypeError, UnicodeDecodeError) as exc:
        return error(str(exc))
    async with app.state.lock:
        started = time.perf_counter()
        try:
            # Intentionally synchronous inside async: MLX stays on the loading thread.
            response = app.state.model.systemone(payload, max_length=MAX_LENGTH, truncate=False)
        except app.state.context_error as exc:
            return error(f"Context limit exceeded; no text was truncated. {exc}", 413)
        except (ValueError, KeyError, TypeError) as exc:
            return error(str(exc))
        except Exception as exc:
            print(f"Inference failed: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
            return error(f"Inference failed: {type(exc).__name__}: {exc}", 500)
        response["usage"]["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
    return JSONResponse(response)


def open_when_ready(port: int):
    """Only this browser helper runs off-thread; it never touches MLX."""
    url = f"http://127.0.0.1:{port}"
    for _ in range(600):
        try:
            with urllib.request.urlopen(f"{url}/health", timeout=1) as response:
                if json.load(response).get("model") == MODEL_NAME:
                    webbrowser.open(url)
                    return
        except (OSError, ValueError, urllib.error.URLError):
            time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--open-browser", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    if args.open_browser:
        threading.Thread(target=open_when_ready, args=(args.port,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=args.port, workers=1, access_log=False)
