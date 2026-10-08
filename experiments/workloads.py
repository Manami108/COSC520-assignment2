"""Precomputed, identical operation sequences for every compared tree."""

from array import array
import random

WORKLOADS = {"uniform", "hotspot", "sequential"}


def search_queries(n, count, workload="uniform", seed=42):
    """Input: size, count, workload, seed. Output: (keys, expected hit count).

    Uniform uses exactly floor(count/2) hits plus disjoint absent keys.
    Hotspot uses 80% probability of keys from the first min(128,n) keys;
    the remaining probability samples the whole set. All requests are hits.
    Sequential cycles over [0,n), also producing only hits.
    """
    if n <= 0 or count <= 0:
        raise ValueError("n and count must be positive")
    if workload not in WORKLOADS:
        raise ValueError("Unknown search workload")
    rng = random.Random(seed)
    if workload == "uniform":
        hits = count // 2
        values = array("q", (rng.randrange(n) for _ in range(hits)))
        values.extend(n + i for i in range(count - hits))
        rng.shuffle(values)
        return values, hits
    if workload == "hotspot":
        return array("q", (rng.randrange(min(n, 128)) if rng.random() < 0.8
                           else rng.randrange(n) for _ in range(count))), count
    return array("q", (i % n for i in range(count))), count


def update_queries(n, count, seed=42):
    """Input: size, requested count, seed. Output: distinct additions/deletions.

    Insert keys [n,n+u) in shuffled order; delete u distinct ORIGINAL keys.
    Both operation counts equal u=min(n,count). Final cardinality equals n.
    """
    if n <= 0 or count <= 0:
        raise ValueError("n and count must be positive")
    count = min(n, count)
    rng = random.Random(seed)
    additions = array("q", range(n, n + count))
    rng.shuffle(additions)
    deletions = array("q", rng.sample(range(n), count))
    return additions, deletions
