"""Benchmark AVL, Treap, and Scapegoat trees with fixed settings.

From the project root:
    python3 -m experiments.benchmark                  # random
    python3 -m experiments.benchmark --order ascending
    python3 -m experiments.benchmark --order all

AI-assisted revision: review and disclose its use as required by your course.
"""

import argparse
import csv
import gc
from pathlib import Path
import random
from time import perf_counter

from structures import TREE_TYPES, make_tree
from structures.base import NULL
from .dataset import ORDERS, SEED, SIZES, make, load

# All benchmark settings are fixed here; only --order is selectable.
REPEATS = 3
QUERIES = 3_000           # successful and unsuccessful searches, each
UPDATES = 1_000           # temporary inserts and deletes; capped at n
SHRINK = True             # also delete 60% of the original keys

FIELDS = (
    "tree", "order", "n", "seed", "repeat", "queries_per_type", "updates",
    "build_s", "search_hit_us", "search_miss_us", "insert_us", "delete_us",
    "height", "mem_mib", "avg_depth", "shrink_deleted", "height_60", "shrink_us",
)


def timed(fn, keys):
    """Time applying fn to every key; return seconds."""
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
    """Average nodes visited to find keys that exist."""
    total = 0
    for key in keys:
        node = tree.root
        while node != NULL:
            total += 1
            if tree.keys[node] == key:
                break
            node = tree.left[node] if key < tree.keys[node] else tree.right[node]
    return total / len(keys)


def bench(n, order, seed=SEED, queries=QUERIES, updates=UPDATES,
          rep=0, shrink=SHRINK):
    """Yield one measurement per tree under identical keys and operations."""
    keys = load(n, order, seed)
    rng = random.Random(seed + rep)

    # The stored keys are even, so odd keys are initially absent.
    hits = [2 * rng.randrange(n) for _ in range(queries)]
    misses = [2 * rng.randrange(n) + 1 for _ in range(queries)]
    count = min(updates, n)
    added = [2 * i + 1 for i in rng.sample(range(n), count)]
    removed = added.copy()
    rng.shuffle(removed)
    probes = [2 * rng.randrange(n) for _ in range(min(1_000, n))]

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
                # Spread deletions across the full original key range.
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
            "mem_mib": round(memory, 3), "shrink_deleted": cut,
            "height_60": height_60, "shrink_us": shrink_us,
        }
        del tree


def result_path(order):
    """Use one CSV per insertion order; there is no experiment tag."""
    return Path("results") / f"bench_{order}.csv"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", choices=(*ORDERS, "all"), default="random")
    args = parser.parse_args()

    orders = ORDERS if args.order == "all" else (args.order,)
    for order in orders:
        dest = result_path(order)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for n in SIZES:
                make(n, order, SEED)  # Reuses an existing dataset automatically.
                for rep in range(REPEATS):
                    for row in bench(n, order, SEED, QUERIES, UPDATES, rep, SHRINK):
                        writer.writerow(row)
                        print(f"{order} n={n:,}, repeat={rep + 1}/{REPEATS}, "
                              f"{row['tree']}: build={row['build_s']:.3f}s, "
                              f"height={row['height']}", flush=True)
                    f.flush()
        print(f"Saved {dest}")


if __name__ == "__main__":
    main()
