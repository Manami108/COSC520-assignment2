"""Run three focused experiments comparing AVL, Treap, and Scapegoat trees.

From the project root:
    python3 -m experiments.benchmark

Optional: run one experiment, or select insertion orders for Experiment 2:
    python3 -m experiments.benchmark --experiment insertion-order --order ascending

All dataset sizes, seeds, query counts and repetitions are set in the code.
AI-assisted revision: review and disclose its use as required by the course.
"""

import argparse
import csv
import gc
from pathlib import Path
import random
from time import perf_counter

from structures import TREE_TYPES, make_tree
from .dataset import (
    DELETION_SIZE, ORDERS, ORDER_SIZE, SCALING_SIZES, SEED, load, make,
)

# Fixed experimental settings (no corresponding command-line arguments).
REPEATS = 3
SEARCH_QUERIES = 50_000
DELETE_FRACTION = 0.60

RESULT_FILE = Path("results") / "benchmarks.csv"
FIELDS = (
    "tree", "order", "n", "repeat", "seed", "build_s",
    "search_hit_us", "height", "memory_mib", "deleted", "bulk_delete_us",
    "height_after_delete",
)


def timed(fn, keys):
    """Call fn on each key and return elapsed seconds, excluding GC pauses."""
    gc_was_on = gc.isenabled()
    gc.disable()
    try:
        start = perf_counter()
        for key in keys:
            fn(key)
        return perf_counter() - start
    finally:
        if gc_was_on:
            gc.enable()


def measure(n, order, repeat, search=False, deletion=False, memory=False,
            only_trees=None, previous=None):
    """Build each tree using identical keys; optionally measure memory or other metrics."""
    make(n, order, SEED)
    keys = load(n, order, SEED)
    rng = random.Random(SEED + 10_000 + repeat)
    probes = [2 * rng.randrange(n) for _ in range(SEARCH_QUERIES)] if search else ()

    delete_keys = ()
    if deletion:
        cut = int(n * DELETE_FRACTION)
        # Same randomly ordered 60% subset for all trees in this repetition.
        # Keeps deletions separate from the timed build and search operations.
        delete_keys = [2 * i for i in rng.sample(range(n), cut)]

    for name in (TREE_TYPES if only_trees is None else only_trees):
        gc.collect()
        tree = make_tree(name, seed=SEED + repeat)
        build_s = timed(tree.insert, keys)
        assert len(tree) == n, (name, "wrong number of keys after build")
        height = tree.height()
        # Measure tree-array storage immediately after build, before deletion.
        memory_mib = round(tree.storage_bytes() / (1024 ** 2), 3) if memory else ""

        # Avoid redoing costly searches/deletions if only memory is missing.
        old = (previous or {}).get((name, order, n, repeat + 1), {})
        search_us = ""
        if search and old.get("search_hit_us", "") == "":
            search_us = round(timed(tree.search, probes) * 1e6 / len(probes), 4)

        removed = ""
        delete_us = ""
        remaining_height = ""
        if deletion and old.get("bulk_delete_us", "") == "":
            delete_us = round(timed(tree.delete, delete_keys) * 1e6 / len(delete_keys), 4)
            removed = len(delete_keys)
            assert len(tree) == n - removed, (name, "wrong number of keys after deletion")
            remaining_height = tree.height()

        record = {
            "tree": name, "order": order, "n": n, "repeat": repeat + 1,
            "seed": SEED, "build_s": round(build_s, 6),
            "search_hit_us": search_us, "height": height,
            "memory_mib": memory_mib, "deleted": removed, "bulk_delete_us": delete_us,
            "height_after_delete": remaining_height,
        }
        # Do not retain a large tree while saving its results.
        del tree
        gc.collect()
        yield record


def key_of(row):
    """Unique identity of a measurement, independent of the metric columns."""
    return row["tree"], row["order"], int(row["n"]), int(row["repeat"])


def read_previous():
    """Load existing data so interrupted experiments can continue."""
    if not RESULT_FILE.exists():
        return {}
    with RESULT_FILE.open(newline="") as f:
        return {key_of(row): row for row in csv.DictReader(f)}


def save_records(records):
    """Atomically save one row per tree/size/order/repetition."""
    RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = RESULT_FILE.with_suffix(".tmp")
    with tmp.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records[k] for k in sorted(records))
    tmp.replace(RESULT_FILE)


def required_complete(row, need_search, need_delete, need_memory):
    """Check whether this record has all measurements needed for this run."""
    return (row is not None
            and row.get("build_s", "") != ""
            and row.get("height", "") != ""
            and (not need_search or row.get("search_hit_us", "") != "")
            and (not need_delete or row.get("bulk_delete_us", "") != "")
            and (not need_memory or row.get("memory_mib", "") != ""))


def jobs(experiment, selected_orders):
    """Combine overlapping experiments so random 1M trees are built once."""
    planned = {}
    if experiment in ("all", "scalability"):
        for n in SCALING_SIZES:
            planned[(n, "random")] = {"search": True, "delete": False}
    if experiment in ("all", "insertion-order"):
        for order in selected_orders:
            planned.setdefault((ORDER_SIZE, order), {"search": False, "delete": False})
    if experiment in ("all", "deletion"):
        task = planned.setdefault((DELETION_SIZE, "random"),
                                  {"search": False, "delete": False})
        task["delete"] = True
    return sorted(planned.items(), key=lambda entry: (entry[0][0], entry[0][1]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment",
                        choices=("all", "scalability", "insertion-order", "deletion"),
                        default="all")
    parser.add_argument("--order", choices=(*ORDERS, "all"), default="all",
                        help="Which order(s) to test in the insertion-order experiment")
    args = parser.parse_args()
    selected_orders = ORDERS if args.order == "all" else (args.order,)

    records = read_previous()
    for (n, order), flags in jobs(args.experiment, selected_orders):
        need_search, need_delete = flags["search"], flags["delete"]
        # Only compare storage at 1M keys with random insertion.
        need_memory = (n == ORDER_SIZE and order == "random")
        for rep in range(REPEATS):
            missing = [tree for tree in TREE_TYPES
                       if not required_complete(records.get((tree, order, n, rep + 1)),
                                                need_search, need_delete, need_memory)]
            if not missing:
                print(f"Already measured: {order}, n={n:,}, repeat={rep + 1}", flush=True)
                continue

            print(f"Measuring {order}, n={n:,}, repeat={rep + 1}/{REPEATS}", flush=True)
            for new in measure(n, order, rep, search=need_search,
                               deletion=need_delete, memory=need_memory,
                               only_trees=missing, previous=records):
                key = key_of(new)
                old = records.get(key, {})
                if required_complete(old, need_search, need_delete, need_memory):
                    continue
                # Preserve previously measured search/deletion fields when adding
                # another experiment to the same tree/size/order/repetition.
                merged = dict(new)
                for metric in ("build_s", "height", "search_hit_us", "memory_mib",
                               "deleted", "bulk_delete_us", "height_after_delete"):
                    if old.get(metric, "") != "" and (metric in ("build_s", "height")
                                                       or merged[metric] == ""):
                        merged[metric] = old[metric]
                records[key] = merged
                save_records(records)
                print(f"  {new['tree']}: build={new['build_s']:.3f}s, "
                      f"height={new['height']}", flush=True)

    print(f"Saved {RESULT_FILE}")

if __name__ == "__main__":
    main()
