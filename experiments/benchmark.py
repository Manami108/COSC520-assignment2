"""Compare AVL, Treap, and Scapegoat on time, height, and search depth.

Run from project root:
    python -m experiments.benchmark --sizes 10000 100000 --order random --repeats 3
    python -m experiments.benchmark --sizes 10000 --order random --shrink
AI-assisted draft: review and disclose its use in the assignment.
"""

import argparse
import csv
import gc
import random
from pathlib import Path
from time import perf_counter

from structures import TREE_TYPES, make_tree
from structures.base import NULL
from .dataset import ORDERS, make, load

FIELDS = ("tree", "order", "n", "seed", "repeat", "queries", "updates",
          "build_s", "search_us", "insert_us", "delete_us", "height",
          "mem_mib", "avg_depth", "height_60", "shrink_us")


def timed(fn, keys):
    """Return batch execution time in seconds, excluding GC pauses."""
    enabled = gc.isenabled()
    gc.disable()
    try:
        start = perf_counter()
        for key in keys:
            fn(key)
        return perf_counter() - start
    finally:
        if enabled:
            gc.enable()


def depth(tree, keys):
    """Return mean nodes visited when searching for existing keys."""
    total = 0
    for key in keys:
        node = tree.root
        while node != NULL:
            total += 1
            if key == tree.keys[node]:
                break
            node = tree.left[node] if key < tree.keys[node] else tree.right[node]
        else:
            raise AssertionError(f"Missing sampled key: {key}")
    return total / len(keys)


def bench(n, order, seed, queries, updates, rep, shrink):
    """Produce one benchmark row for each tree using identical operations."""
    keys = load(n, order, seed)
    rng = random.Random(seed + 1000 + rep)
    lookups = [2 * rng.randrange(n) + (i % 2) for i in range(queries)]
    count = min(updates, n)
    added = [2 * i + 1 for i in rng.sample(range(n), count)]
    removed = added.copy()
    rng.shuffle(removed)
    probes = [2 * rng.randrange(n) for _ in range(min(1000, n))]

    for name in TREE_TYPES:
        gc.collect()
        tree = make_tree(name, seed=seed + rep)
        build = timed(tree.insert, keys)
        if len(tree) != n:
            raise AssertionError(f"{name}: build size mismatch")
        height = tree.height()
        avg_depth = depth(tree, probes)
        memory = tree.storage_bytes() / (1024 * 1024)
        search = timed(tree.search, lookups)
        insert = timed(tree.insert, added)
        delete = timed(tree.delete, removed)
        if len(tree) != n:
            raise AssertionError(f"{name}: updates changed final size")

        height_60, shrink_us = "", ""
        if shrink:
            cut = n * 60 // 100
            if cut:
                seconds = timed(tree.delete, range(0, 2 * cut, 2))
                if len(tree) != n - cut:
                    raise AssertionError(f"{name}: shrink size mismatch")
                height_60 = tree.height()
                shrink_us = round(seconds * 1e6 / cut, 4)

        yield {"tree": name, "order": order, "n": n, "seed": seed,
               "repeat": rep, "queries": queries, "updates": count,
               "build_s": round(build, 6),
               "search_us": round(search * 1e6 / queries, 4),
               "insert_us": round(insert * 1e6 / count, 4),
               "delete_us": round(delete * 1e6 / count, 4),
               "height": height, "avg_depth": round(avg_depth, 3),
               "mem_mib": round(memory, 3),
               "height_60": height_60, "shrink_us": shrink_us}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[10000, 100000])
    parser.add_argument("--order", choices=ORDERS, default="random")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--queries", type=int, default=3000)
    parser.add_argument("--updates", type=int, default=1000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--shrink", action="store_true", help="Also delete 60%% of original keys")
    args = parser.parse_args()
    if any(n < 1 for n in args.sizes) or min(args.queries, args.updates, args.repeats) < 1:
        parser.error("sizes, queries, updates and repeats must be positive")

    Path("results").mkdir(exist_ok=True)
    dest = Path("results") / f"bench_{args.order}.csv"
    with dest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for n in args.sizes:
            make(n, args.order, args.seed)
            print(f"Benchmark n={n:,}, order={args.order}", flush=True)
            for rep in range(args.repeats):
                for row in bench(n, args.order, args.seed, args.queries,
                                 args.updates, rep, args.shrink):
                    writer.writerow(row)
                    print(f"  {row['tree']}: {row['build_s']:.4f}s, "
                          f"height={row['height']}, depth={row['avg_depth']:.2f}")
    print(f"Saved {dest}")


if __name__ == "__main__":
    main()
