"""Run every benchmark in a fresh Python subprocess and save raw observations."""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

from structures import TREE_TYPES
from .dataset import MAX_N, ensure_dataset
from .workloads import WORKLOADS
from .summarize import summarize

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["algorithm", "n", "order", "workload", "repeat", "seed", "treap_seed",
          "operation", "operations", "successes", "seconds", "us_per_operation",
          "tree_array_bytes", "dataset_sha256", "warmup_queries", "job_peak_rss_bytes"]


def read_config(path):
    """Input: JSON config path. Output: validated config with explicit defaults."""
    config = json.loads(Path(path).read_text())
    defaults = {"algorithms": list(TREE_TYPES), "orders": ["random"],
                "workloads": ["uniform"], "repeats": 3, "queries": 10000,
                "updates": 10000, "warmup": 1000, "seed": 42, "validate_limit": 100000}
    unknown = set(config) - (set(defaults) | {"sizes"})
    if unknown:
        raise ValueError(f"Unknown config fields: {sorted(unknown)}")
    config = defaults | config
    for field in ("repeats", "queries", "updates"):
        if type(config[field]) is not int or config[field] <= 0:
            raise ValueError(f"{field} must be a positive integer")
    for field in ("warmup", "validate_limit", "seed"):
        if type(config[field]) is not int or config[field] < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    if not config.get("sizes") or any(type(n) is not int or not 1 <= n <= MAX_N for n in config["sizes"]):
        raise ValueError("sizes must contain positive integers below the node-index limit")
    for field, options in (("algorithms", set(TREE_TYPES)),
                           ("orders", {"random", "ascending", "descending"}),
                           ("workloads", WORKLOADS)):
        if not config[field] or any(value not in options for value in config[field]):
            raise ValueError(f"Invalid {field}: allowed {sorted(options)}")
    for field in ("sizes", "algorithms", "orders", "workloads"):
        if len(set(config[field])) != len(config[field]):
            raise ValueError(f"Duplicate entries in {field}")
    return config


def source_hash():
    """Input: none. Output: SHA-256 of algorithm and experiment Python source."""
    digest = hashlib.sha256()
    for directory in ("structures", "experiments"):
        for path in sorted((ROOT / directory).glob("*.py")):
            digest.update(str(path.relative_to(ROOT)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def job_key(row):
    """Input: raw row/job. Output: identity shared by the four operation rows."""
    return (row["algorithm"], int(row["n"]), row["order"], row["workload"], int(row["repeat"]))


def run(config, output, data_directory, resume=False):
    """Input: config/paths/resume flag. Output: results saved incrementally.

    Resume requires identical config, source, interpreter and platform.
    Each successful job is flushed; incomplete jobs are rerun on resume.
    """
    output, data_directory = Path(output).resolve(), Path(data_directory).resolve()
    output.mkdir(parents=True, exist_ok=True)
    raw_path, meta_path = output / "raw.csv", output / "metadata.json"
    environment = {"python": sys.version, "platform": platform.platform(),
                   "machine": platform.machine(), "processor": platform.processor(),
                   "cpu_count": os.cpu_count(), "clock": "time.perf_counter_ns",
                   "source_sha256": source_hash()}
    existing, completed = [], set()
    if raw_path.exists() or meta_path.exists():
        if not resume:
            raise FileExistsError("Result files exist; use --resume or choose a new --output")
        if not raw_path.exists() or not meta_path.exists():
            raise ValueError("Cannot resume without both raw.csv and metadata.json")
        old = json.loads(meta_path.read_text())
        if old["config"] != config or old["environment"] != environment:
            raise ValueError("Resume rejected: config, source, or environment changed")
        with raw_path.open(newline="") as stream:
            existing = list(csv.DictReader(stream))
        operations = {}
        for row in existing:
            operations.setdefault(job_key(row), []).append(row["operation"])
        completed = {key for key, ops in operations.items()
                     if sorted(ops) == ["build", "delete", "insert", "search"]}
        existing = [row for row in existing if job_key(row) in completed]
        metadata = old
    else:
        metadata = {"config": config, "environment": environment,
                    "created_utc": datetime.now(timezone.utc).isoformat(),
                    "datasets": {}, "status": "running"}
    metadata["status"] = "running"
    meta_path.write_text(json.dumps(metadata, indent=2) + "\n")
    total = len(config["sizes"]) * len(config["orders"]) * len(config["workloads"])
    total *= config["repeats"] * len(config["algorithms"])
    done = len(completed)
    with raw_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(existing)
        stream.flush()
        for n in config["sizes"]:
            for order in config["orders"]:
                print(f"Preparing/reusing dataset n={n:,}, order={order}", flush=True)
                dataset = ensure_dataset(data_directory, n, order, config["seed"])
                manifest = json.loads(dataset.with_suffix(dataset.suffix + ".json").read_text())
                metadata["datasets"][dataset.name] = manifest
                meta_path.write_text(json.dumps(metadata, indent=2) + "\n")
                for workload in config["workloads"]:
                    for repeat in range(config["repeats"]):
                        algorithms = config["algorithms"].copy()
                        random.Random(config["seed"] + n + repeat).shuffle(algorithms)
                        for algorithm in algorithms:
                            job = {"algorithm": algorithm, "n": n, "order": order,
                                   "workload": workload, "repeat": repeat,
                                   "dataset": str(dataset), "dataset_sha256": manifest["sha256"],
                                   "treap_seed": config["seed"] + repeat * 1009,
                                   **{key: config[key] for key in
                                      ("queries", "updates", "warmup", "seed", "validate_limit")}}
                            if job_key(job) in completed:
                                continue
                            print(f"[{done + 1}/{total}] {algorithm}, n={n:,}, {order}, "
                                  f"{workload}, repeat={repeat + 1}", flush=True)
                            start = time.perf_counter()
                            process = subprocess.run(
                                [sys.executable, "-m", "experiments.worker", "--job-json", json.dumps(job)],
                                cwd=ROOT, capture_output=True, text=True,
                            )
                            if process.returncode:
                                metadata["status"] = "failed"
                                metadata["failed_job"] = job
                                meta_path.write_text(json.dumps(metadata, indent=2) + "\n")
                                raise RuntimeError(f"Worker failed:\n{process.stderr}")
                            rows = json.loads(process.stdout)
                            writer.writerows(rows)
                            stream.flush()
                            done += 1
                            print(f"  complete in {time.perf_counter() - start:.2f}s", flush=True)
    metadata.pop("failed_job", None)
    metadata["status"] = "complete"
    metadata["completed_jobs"] = done
    metadata["finished_utc"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(metadata, indent=2) + "\n")
    summarize(raw_path, output)
    print(f"Saved {raw_path} and {output / 'summary.csv'}", flush=True)


def main():
    """Input: CLI config/output paths. Output: CSVs and reproducibility metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/quick.json")
    parser.add_argument("--output", type=Path, default=Path("results/quick"))
    parser.add_argument("--data-directory", type=Path, default=Path("data"))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(read_config(args.config), args.output, args.data_directory, args.resume)


if __name__ == "__main__":
    main()
