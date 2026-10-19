"""Generate reproducible integer datasets for the tree benchmarks.

Run from the project root: python -m experiments.dataset --sizes 10000 100000
AI-assisted draft: review and disclose its use in the assignment.
"""

import argparse
import random
from array import array
from pathlib import Path

DATA_DIR = Path("data")
ORDERS = ("random", "ascending", "descending")


def path(n, order, seed, folder=DATA_DIR):
    """Input: dataset settings. Output: path to its binary file."""
    return Path(folder) / f"keys_{order}_{n}_s{seed}.bin"


def make(n, order="random", seed=42, folder=DATA_DIR):
    """Input: count, insertion order, seed. Output: binary dataset path.

    Keys are unique even integers, leaving odd integers for update tests.
    Stored as native 64-bit signed integers; random data uses about 8n bytes
    of RAM while shuffling. Ordered datasets are written in small chunks.
    """
    if not 0 < n <= ((1 << 63) - 1) // 2:
        raise ValueError("n must be positive and fit into signed 64-bit keys")
    if order not in ORDERS:
        raise ValueError(f"order must be one of {ORDERS}")

    dest = path(n, order, seed, folder)
    if dest.is_file() and dest.stat().st_size == n * 8:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)

    with dest.open("wb") as f:
        if order == "random":
            keys = array("q", (2 * i for i in range(n)))
            random.Random(seed).shuffle(keys)
            keys.tofile(f)
        else:
            for start in range(0, n, 65536):
                stop = min(start + 65536, n)
                indices = (range(start, stop) if order == "ascending"
                           else range(n - 1 - start, n - 1 - stop, -1))
                array("q", (2 * i for i in indices)).tofile(f)
    return dest


def load(n, order="random", seed=42, folder=DATA_DIR):
    """Input: dataset settings. Output: array of keys, or error if missing."""
    source = path(n, order, seed, folder)
    if not source.is_file():
        raise FileNotFoundError(f"Missing {source}; run experiments.dataset first")
    keys = array("q")
    with source.open("rb") as f:
        keys.fromfile(f, n)
        if f.read(1):
            raise ValueError(f"Unexpected extra bytes in {source}")
    return keys


def main():
    """Input: CLI options. Output: dataset files in data/."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[10000, 100000])
    parser.add_argument("--order", choices=ORDERS, default="random")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    for n in args.sizes:
        dest = make(n, args.order, args.seed)
        print(f"{dest}  ({dest.stat().st_size / 1048576:.1f} MiB)")


if __name__ == "__main__":
    main()
