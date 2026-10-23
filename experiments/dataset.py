# This file generate integer datasets
import argparse
from array import array
from pathlib import Path
import random

DATA_DIR = Path("data")
ORDERS = ("random", "ascending", "descending")
SEED = 42

# Experiment 1 - random insertion with increasing dataset sizes
SCALING_SIZES = (1_000, 10_000, 100_000, 1_000_000, 10_000_000)

# Experiments 2 and 3 - fixed-size comparisons at 10M keys
ORDER_SIZE = 10_000_000
DELETION_SIZE = 10_000_000

def path(n, order, folder=DATA_DIR):
    return Path(folder) / f"{order}_{n}.bin"

def make(n, order="random", seed=SEED, folder=DATA_DIR):
    # The code generates n distinct even-numbered keys in the specified order and reuses an existing file if its size matches n * 8 bytes.
    dest = path(n, order, folder)
    if dest.exists() and dest.stat().st_size == n * 8:
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as f:
        if order == "random":
            # It shuffles the keys using a fixed random seed
            values = array("q", range(0, 2 * n, 2))
            random.Random(seed).shuffle(values)
            values.tofile(f)
        else:
            # It writes ordered keys in batches to limit memory usage
            for start in range(0, n, 65_536):
                stop = min(start + 65_536, n)
                if order == "ascending":
                    positions = range(start, stop)
                else:
                    positions = range(n - 1 - start, n - 1 - stop, -1)
                array("q", (2 * i for i in positions)).tofile(f)
    return dest

def load(n, order="random", seed=SEED, folder=DATA_DIR):
    # It loads n integer keys from the binary dataset
    keys = array("q")
    with path(n, order, folder).open("rb") as f:
        keys.fromfile(f, n)
    return keys

def main():
    # this block generates the required datasets. 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", choices=(*ORDERS, "all"), default="all")
    args = parser.parse_args()
    requested = ORDERS if args.order == "all" else (args.order,)
    for order in requested:
        sizes = set(SCALING_SIZES) if order == "random" else set()
        sizes.add(ORDER_SIZE)
        if order == "random":
            sizes.add(DELETION_SIZE)
        for n in sorted(sizes):
            print(f"Dataset: {make(n, order)}", flush=True)

if __name__ == "__main__":
    main()
