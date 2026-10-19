"""Benchmark insert (build), search, extra insert, and delete for three trees.

Run from project root: python -m experiments.benchmark --sizes 10000 100000
AI-assisted draft: review and disclose its use in the assignment.
"""

import argparse
import csv
import gc
import random
from pathlib import Path
from time import perf_counter

from structures import TREE_TYPES, make_tree
from .dataset import ORDERS, load

FIELDS = ("tree", "order", "n", "seed", "repeat", "queries", "updates",
          "build_s", "search_us", "insert_us", "delete_us", "height", "mem_mib")


def time_ops(fn, keys):
    """Input: a tree operation and keys. Output: elapsed seconds."""
    start = perf_counter()
    for key in keys:
        fn(key)
    return perf_counter() - start


def bench(n, order, seed, queries, updates, rep):
    """Input: workload settings. Output: one result row per tree."""
    keys = load(n, order, seed)
    rng = random.Random(seed + 1000)
    # Each lookup is an existing even key or an absent odd key (50/50).
    lookups = [2 * rng.randrange(n) + (i % 2) for i in range(queries)]
    count = min(updates, n)
    added = [2 * i + 1 for i in rng.sample(range(n), count)]
    removed = added.copy()
    rng.shuffle(removed)

    for name in TREE_TYPES:
        gc.collect()  # Do not include cleanup from the previous tree in timings.
        tree = make_tree(name, seed=seed + rep)
        build = time_ops(tree.insert, keys)
        height = tree.height()  # Diagnostics are outside timed operations.
        memory = tree.storage_bytes() / 1048576
        search = time_ops(tree.search, lookups)
        insert = time_ops(tree.insert, added)
        delete = time_ops(tree.delete, removed)
        if len(tree) != n:  # A quick integrity check, not a timed validation.
            raise AssertionError(f"{name}: tree size changed unexpectedly")
        yield {
            "tree": name, "order": order, "n": n, "seed": seed,
            "repeat": rep, "queries": queries, "updates": count,
            "build_s": round(build, 6),
            "search_us": round(search * 1e6 / queries, 4),
            "insert_us": round(insert * 1e6 / count, 4),
            "delete_us": round(delete * 1e6 / count, 4),
            "height": height, "mem_mib": round(memory, 3),
        }
        del tree

def main():
    """Input: CLI settings. Output: CSV results and progress in terminal."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[10000, 100000])
    parser.add_argument("--order", choices=ORDERS, default="random")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--queries", type=int, default=3000)
    parser.add_argument("--updates", type=int, default=1000)
    parser.add_argument("--repeats", type=int, default=1)
    args = parser.parse_args()
    if any(n < 1 for n in args.sizes) or min(args.queries, args.updates, args.repeats) < 1:
        parser.error("sizes, queries, updates, and repeats must all be positive")

    Path("results").mkdir(exist_ok=True)
    dest = Path("results") / f"bench_{args.order}.csv"
    with dest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for n in args.sizes:
            print(f"Benchmarking n={n:,} ({args.order}) ...", flush=True)
            for rep in range(args.repeats):
                for row in bench(n, args.order, args.seed, args.queries, args.updates, rep):
                    writer.writerow(row)
                    f.flush()
                    print(f"  {row['tree']:9s} build={row['build_s']:8.3f}s "
                          f"search={row['search_us']:8.2f} us/op", flush=True)
    print(f"Saved {dest}")

if __name__ == "__main__":
    main()
