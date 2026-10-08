"""One isolated benchmark job; stdout is JSON, suitable for the runner."""

import argparse
import gc
import json
import platform
import sys
import time

from structures import make_tree
from structures.base import PackedBST
from .dataset import load_dataset
from .workloads import search_queries, update_queries


def timed_batch(method, values):
    """Input: method/keys. Output: elapsed seconds and successful return count.

    Includes Python iteration/dispatch, but not dataset/workload preparation.
    Disable cyclic GC only while timing and restore its previous state.
    """
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        start = time.perf_counter_ns()
        successes = 0
        for value in values:
            successes += method(value)
        elapsed = (time.perf_counter_ns() - start) / 1_000_000_000
    finally:
        if was_enabled:
            gc.enable()
    return elapsed, successes


def peak_rss_bytes():
    """Input: none. Output: OS peak resident bytes or None when unavailable."""
    try:
        import resource
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return value if sys.platform == "darwin" else value * 1024
    except ImportError:
        return None


def run_job(job):
    """Input: benchmark job dictionary. Output: four verified metric rows.

    A job builds a fresh tree, warms/searches one workload, then inserts new
    keys and deletes original keys. Search workloads never share a tree.
    """
    values = load_dataset(job["dataset"])
    n = len(values)
    if n != job["n"]:
        raise ValueError("Dataset size differs from the requested benchmark size")
    queries, expected = search_queries(n, job["queries"], job["workload"], job["seed"])
    additions, deletions = update_queries(n, job["updates"], job["seed"] + 1)
    tree = make_tree(job["algorithm"], seed=job["treap_seed"])
    metrics = []

    def record(operation, elapsed, count, successes, storage):
        """Input: measured values. Output: append a normalized result row."""
        metrics.append({
            "algorithm": job["algorithm"], "n": n, "order": job["order"],
            "workload": job["workload"], "repeat": job["repeat"],
            "seed": job["seed"], "treap_seed": job["treap_seed"],
            "operation": operation, "operations": count, "successes": successes,
            "seconds": elapsed, "us_per_operation": elapsed * 1_000_000 / count,
            "tree_array_bytes": storage, "dataset_sha256": job["dataset_sha256"],
            "warmup_queries": min(job["warmup"], len(queries)),
        })

    elapsed, successes = timed_batch(tree.insert, values)
    if successes != n or len(tree) != n:
        raise AssertionError("Build failed to insert all distinct keys")
    storage = tree.storage_bytes()
    record("build", elapsed, n, successes, storage)
    if n <= job["validate_limit"]:
        tree.validate()
    else:
        # Fixed known members check large builds without an O(n) debug set.
        for index in range(min(n, 100)):
            if not PackedBST.contains(tree, int(values[(index * 104729) % n])):
                raise AssertionError("A large-build member probe failed")

    for value in queries[:job["warmup"]]:
        tree.contains(value)
    elapsed, successes = timed_batch(tree.contains, queries)
    if successes != expected:
        raise AssertionError("Search hit count differs from the known answer")
    record("search", elapsed, len(queries), successes, storage)

    elapsed, successes = timed_batch(tree.insert, additions)
    if successes != len(additions) or len(tree) != n + len(additions):
        raise AssertionError("Insert batch failed")
    record("insert", elapsed, len(additions), successes, tree.storage_bytes())
    elapsed, successes = timed_batch(tree.delete, deletions)
    if successes != len(deletions) or len(tree) != n:
        raise AssertionError("Delete batch failed")
    record("delete", elapsed, len(deletions), successes, tree.storage_bytes())
    if n <= job["validate_limit"]:
        tree.validate()
    for value in additions:
        if not tree.contains(value):
            raise AssertionError("An added key disappeared")
    for value in deletions:
        if tree.contains(value):
            raise AssertionError("A deleted key remains")
    rss = peak_rss_bytes()
    for metric in metrics:
        metric["job_peak_rss_bytes"] = rss
    return metrics


def main():
    """Input: a JSON job via CLI. Output: JSON metrics, or nonzero on failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-json", required=True)
    args = parser.parse_args()
    print(json.dumps(run_job(json.loads(args.job_json))))


if __name__ == "__main__":
    main()
