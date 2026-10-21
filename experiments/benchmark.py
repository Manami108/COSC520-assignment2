"""Benchmark AVL, Treap, and Scapegoat trees.

Run from the project root, for example:
    python -m experiments.benchmark --sizes 10000 100000 --order random --repeats 3 --shrink --tag pilot
AI-assisted revision: review and disclose its use in the assignment report.
"""

import argparse
import csv
import gc
from pathlib import Path
import random
from time import perf_counter

from structures import TREE_TYPES, make_tree
from structures.base import NULL
from .dataset import ORDERS, make, load

FIELDS = (
    "tree", "order", "n", "seed", "repeat", "queries_per_type", "updates",
    "build_s", "search_hit_us", "search_miss_us", "insert_us", "delete_us",
    "height", "mem_mib", "avg_depth", "shrink_deleted", "height_60", "shrink_us",
)


def timed(fn, keys):
    """Return the time in seconds to apply fn to every key."""
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        start = perf_counter()
        for key in keys:
            fn(key)
        return perf_counter() - start
    finally:
        if was_enabled:
            gc.enable()


def depth(tree, keys):
    """Return the average search depth for keys known to exist."""
    total = 0
    for key in keys:
        node = tree.root
        while node != NULL:
            total += 1
            if tree.keys[node] == key:
                break
            node = tree.left[node] if key < tree.keys[node] else tree.right[node]
    return total / len(keys)


def bench(n, order, seed, queries, updates, rep, shrink):
    """Measure each tree using the same keys and operations."""
    keys = load(n, order, seed)
    rng = random.Random(seed + rep)

    # Original keys are even; odd numbers are absent until insertion.
    hits = [2 * rng.randrange(n) for _ in range(queries)]
    misses = [2 * rng.randrange(n) + 1 for _ in range(queries)]
    count = min(updates, n)
    added = [2 * i + 1 for i in rng.sample(range(n), count)]
    removed = added.copy()
    rng.shuffle(removed)
    probes = [2 * rng.randrange(n) for _ in range(min(1000, n))]

    for name in TREE_TYPES:
        gc.collect()
        tree = make_tree(name, seed=seed + rep)

        build = timed(tree.insert, keys)
        assert len(tree) == n
        height = tree.height()
        avg_depth = depth(tree, probes)
        memory = tree.storage_bytes() / (1024 * 1024)

        hit_s = timed(tree.search, hits)
        miss_s = timed(tree.search, misses)
        insert = timed(tree.insert, added)
        delete = timed(tree.delete, removed)
        assert len(tree) == n

        cut, height_60, shrink_us = 0, "", ""
        if shrink:
            cut = n * 60 // 100
            if cut:
                # Spread selected keys across the whole original key range.
                # This generator avoids creating another large list.
                bulk_keys = (2 * (i * n // cut) for i in range(cut))
                seconds = timed(tree.delete, bulk_keys)
                assert len(tree) == n - cut
                height_60 = tree.height()
                shrink_us = round(seconds * 1e6 / cut, 4)

        yield {
            "tree": name, "order": order, "n": n, "seed": seed,
            "repeat": rep, "queries_per_type": queries, "updates": count,
            "build_s": round(build, 6),
            "search_hit_us": round(hit_s * 1e6 / queries, 4),
            "search_miss_us": round(miss_s * 1e6 / queries, 4),
            "insert_us": round(insert * 1e6 / count, 4),
            "delete_us": round(delete * 1e6 / count, 4),
            "height": height, "avg_depth": round(avg_depth, 3),
            "mem_mib": round(memory, 3),
            "shrink_deleted": cut, "height_60": height_60,
            "shrink_us": shrink_us,
        }


def result_path(order, tag=""):
    """Return the output CSV path, optionally labeled by experiment."""
    suffix = f"_{tag}" if tag else ""
    return Path("results") / f"bench_{order}{suffix}.csv"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[10000, 100000])
    parser.add_argument("--order", choices=ORDERS, default="random")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--queries", type=int, default=3000)
    parser.add_argument("--updates", type=int, default=1000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--shrink", action="store_true")
    parser.add_argument("--tag", default="")
    args = parser.parse_args()

    # These quantities are used as divisors in per-operation timings.
    if any(n < 1 for n in args.sizes) or min(args.queries, args.updates, args.repeats) < 1:
        parser.error("sizes, queries, updates and repeats must be positive")

    dest = result_path(args.order, args.tag)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for n in args.sizes:
            make(n, args.order, args.seed)
            for rep in range(args.repeats):
                for row in bench(n, args.order, args.seed, args.queries,
                                 args.updates, rep, args.shrink):
                    writer.writerow(row)
                    print(f"n={n:,}, repeat={rep + 1}, {row['tree']}: "
                          f"build={row['build_s']:.3f}s, height={row['height']}",
                          flush=True)
                f.flush()
    print(f"Saved {dest}")


if __name__ == "__main__":
    main()
