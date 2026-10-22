"""Create datasets for AVL, Treap, and Scapegoat experiments.

From the project root:
    python3 -m experiments.dataset                  # random
    python3 -m experiments.dataset --order ascending
    python3 -m experiments.dataset --order all

AI-assisted revision: review and disclose its use as required by your course.
"""

import argparse
from array import array
from pathlib import Path
import random

# Fixed settings for both dataset.py and benchmark.py. Change sizes here.
SIZES = (100, 1_000, 100_000, 1_000_000, 10_000_000)
SEED = 42

DATA_DIR = Path("data")
ORDERS = ("random", "ascending", "descending")


def path(n, order, seed=SEED, folder=DATA_DIR):
    """Filename for a particular dataset."""
    return Path(folder) / f"keys_{order}_{n}_s{seed}.bin"


def make(n, order="random", seed=SEED, folder=DATA_DIR):
    """Save n distinct even keys in the requested insertion order."""
    dest = path(n, order, seed, folder)
    if dest.exists() and dest.stat().st_size == n * 8:
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as f:
        if order == "random":
            keys = array("q", (2 * i for i in range(n)))
            random.Random(seed).shuffle(keys)
            keys.tofile(f)
        else:
            # Write sorted keys in chunks to avoid holding another big list.
            for start in range(0, n, 65536):
                stop = min(start + 65536, n)
                if order == "ascending":
                    indices = range(start, stop)
                else:
                    indices = range(n - 1 - start, n - 1 - stop, -1)
                array("q", (2 * i for i in indices)).tofile(f)
    return dest


def load(n, order="random", seed=SEED, folder=DATA_DIR):
    """Load keys as a compact array of 64-bit integers."""
    keys = array("q")
    with path(n, order, seed, folder).open("rb") as f:
        keys.fromfile(f, n)
    return keys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", choices=(*ORDERS, "all"), default="random")
    args = parser.parse_args()

    orders = ORDERS if args.order == "all" else (args.order,)
    for order in orders:
        for n in SIZES:
            dest = make(n, order, SEED)
            print(f"Saved {dest}", flush=True)


if __name__ == "__main__":
    main()
