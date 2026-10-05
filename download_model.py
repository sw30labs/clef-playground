"""Download the pinned Clef checkpoint, or verify a completed local download."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true", help="Check file sizes without network access")
    args = parser.parse_args()
    manifest = json.loads((HERE / "model-manifest.json").read_text())
    destination = HERE / "model"
    if not args.verify_only:
        os.environ.setdefault("HF_HOME", str(HERE / ".hf-cache"))
        from huggingface_hub import snapshot_download

        size_gb = sum(item["bytes"] for item in manifest["files"]) / 1e9
        print(f"Downloading {manifest['repo_id']} ({size_gb:.1f} GB)", flush=True)
        print(f"Revision: {manifest['revision']}", flush=True)
        snapshot_download(
            manifest["repo_id"], revision=manifest["revision"], local_dir=destination,
            allow_patterns=[item["name"] for item in manifest["files"]], max_workers=8,
        )
    incomplete = []
    for item in manifest["files"]:
        path = destination / item["name"]
        if not path.is_file() or path.stat().st_size != item["bytes"]:
            incomplete.append(item["name"])
    if incomplete:
        parser.exit(1, "Missing or incomplete model files: " + ", ".join(incomplete) + "\n")
    print(f"Verified sizes of all {len(manifest['files'])} model files. Run ./start.command to begin.")


if __name__ == "__main__":
    main()
