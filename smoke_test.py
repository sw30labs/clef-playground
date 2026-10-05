#!/usr/bin/env python3
"""Run three synthetic text checks against a local MLX Clef checkpoint.

This is a functional smoke test, not an accuracy or throughput benchmark.
Score expectations refer to the most probable level, not the weighted score.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
import json
import math
from pathlib import Path
import platform
import sys
import time


HERE = Path(__file__).resolve().parent


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(request, response, expected):
    checks = []

    def check(name, passed, actual=None, target=None):
        checks.append({"check": name, "passed": bool(passed), "actual": actual, "expected": target})

    answers = response.get("answers", {})
    check("answer_fields", isinstance(answers, dict) and set(answers) == set(expected),
          list(answers) if isinstance(answers, dict) else answers, list(expected))
    if not isinstance(answers, dict):
        return checks
    for field, target in expected.items():
        question = request["questions"][field]
        answer = answers.get(field)
        kind = question["type"]
        check(f"{field}.type", isinstance(answer, dict) and answer.get("type") == kind,
              answer.get("type") if isinstance(answer, dict) else answer, kind)
        if not isinstance(answer, dict):
            continue
        if kind == "noul":
            probability = answer.get("noul")
            valid = finite_number(probability) and 0 <= probability <= 1
            check(f"{field}.probability", valid, probability, "finite, within [0, 1]")
            # SystemOne returns only P(true); P(false) is its complement.
            predicted = probability > 0.5 if valid and probability != 0.5 else None
            check(f"{field}.expected_boolean", predicted is target, predicted, target)
            continue
        option_ids = (set(question["criteria"]) if kind == "choice"
                      else {str(i) for i in range(len(question["criteria"]))})
        probabilities = answer.get("probabilities")
        valid_keys = isinstance(probabilities, dict) and set(probabilities) == option_ids
        check(f"{field}.probability_options", valid_keys,
              list(probabilities) if isinstance(probabilities, dict) else probabilities, sorted(option_ids))
        valid_values = (valid_keys and all(finite_number(p) and 0 <= p <= 1
                                          for p in probabilities.values()))
        check(f"{field}.probability_values", valid_values, probabilities, "finite, within [0, 1]")
        # The adapter rounds probabilities to four decimals independently.
        total = sum(probabilities.values()) if valid_values else None
        tolerance = len(option_ids) * 0.00005 + 0.000001
        check(f"{field}.probability_sum", total is not None and abs(total - 1) <= tolerance,
              total, {"sum": 1.0, "absolute_tolerance": tolerance})
        confidence = answer.get("confidence")
        check(f"{field}.confidence", finite_number(confidence) and 0 <= confidence <= 1,
              confidence, "finite, within [0, 1]")
        winners = []
        if valid_values:
            maximum = max(probabilities.values())
            winners = [key for key, probability in probabilities.items() if probability == maximum]
            check(f"{field}.confidence_matches_probabilities",
                  finite_number(confidence) and abs(confidence - maximum) <= 0.000001,
                  confidence, maximum)
        check(f"{field}.expected_top_option", winners == [target], winners, [target])
        if kind == "choice":
            check(f"{field}.choice", answer.get("choice") == target, answer.get("choice"), target)
        else:
            score = answer.get("score")
            maximum_score = len(question["criteria"]) - 1
            check(f"{field}.score_range", finite_number(score) and 0 <= score <= maximum_score,
                  score, [0, maximum_score])
            if valid_values:
                weighted_score = sum(int(option) * probability for option, probability in probabilities.items())
                score_tolerance = 0.00005 * (1 + sum(range(len(option_ids)))) + 0.000001
                check(f"{field}.score_matches_probabilities",
                      finite_number(score) and abs(score - weighted_score) <= score_tolerance,
                      score, {"weighted_score": weighted_score, "absolute_tolerance": score_tolerance})
    return checks


def json_safe(value):
    """Keep invalid model numbers inspectable without emitting invalid JSON."""
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Existing local MLX checkpoint directory")
    parser.add_argument("--output", required=True, type=Path, help="JSON results file")
    args = parser.parse_args()
    model_path = Path(args.model).expanduser().resolve()
    output = args.output.expanduser().resolve()
    packages = {}
    for name in ("mlx", "mlx-lm", "mlx-vlm", "transformers"):
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = None
    report = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_argument": args.model,
        "model_path": str(model_path),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": packages,
        "scope": "Three synthetic text examples; functional smoke test only. No accuracy or performance benchmark claims.",
        "truncate": False,
        "load_seconds": None,
        "peak_memory_bytes": None,
        "cases": [],
        "status": "running",
    }
    manifest = HERE / "model-manifest.json"
    if manifest.exists():
        report["model_provenance"] = json.loads(manifest.read_text())

    def save():
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(json_safe(report), indent=2, allow_nan=False) + "\n")

    save()
    load_started = None
    mx = None
    try:
        if not model_path.is_dir():
            raise ValueError(f"Local model directory does not exist: {model_path}")
        for item in report.get("model_provenance", {}).get("files", []):
            path = model_path / item["name"]
            if not path.is_file() or path.stat().st_size != item["bytes"]:
                raise ValueError(f"Model download is incomplete: {item['name']}")
        sys.path.insert(0, str(HERE / "vendor"))
        import mlx.core as mx
        import clef_mlx

        load_started = time.perf_counter()
        model = clef_mlx.load(str(model_path))
        report["load_seconds"] = time.perf_counter() - load_started
        report["peak_memory_bytes"] = mx.get_peak_memory()
        save()
        for example_path in sorted((HERE / "examples").glob("*.json")):
            example = json.loads(example_path.read_text())
            request = example["request"]
            request["model"] = report.get("model_provenance", {}).get("repo_id", model_path.name)
            case = {
                "name": example["name"], "source": str(example_path),
                "request": request, "expected": example["expected"],
                "status": "running",
            }
            report["cases"].append(case)
            started = time.perf_counter()
            try:
                case["response"] = model.systemone(request, truncate=False)
                case["inference_seconds"] = time.perf_counter() - started
                case["checks"] = validate(request, case["response"], example["expected"])
                case["status"] = "passed" if all(check["passed"] for check in case["checks"]) else "failed"
            except Exception as error:
                case["inference_seconds"] = time.perf_counter() - started
                case["status"] = "error"
                case["error"] = f"{type(error).__name__}: {error}"
            report["peak_memory_bytes"] = mx.get_peak_memory()
            save()
            print(f"{case['name']}: {case['status']} ({case['inference_seconds']:.3f}s)", flush=True)
        report["passed_cases"] = sum(case["status"] == "passed" for case in report["cases"])
        report["total_cases"] = len(report["cases"])
        report["status"] = "passed" if report["total_cases"] == 3 and report["passed_cases"] == 3 else "failed"
    except Exception as error:
        report["status"] = "error"
        report["error"] = f"{type(error).__name__}: {error}"
        if load_started is not None and report["load_seconds"] is None:
            report["load_seconds"] = time.perf_counter() - load_started
    finally:
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        save()
    print(f"Results: {output}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
