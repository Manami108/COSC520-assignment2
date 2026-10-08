"""Create/read portable gzip-compressed little-endian uint32 datasets."""

import argparse
from array import array
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys

MAX_N = (1 << 31) - 1


def sha256_file(path):
    """Input: file path. Output: streaming SHA-256 hex digest."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_path(directory, n, order, seed):
    """Input: directory and generation parameters. Output: canonical path."""
    return Path(directory) / f"keys_{n}_{order}_seed{seed}.u32.gz"


def generate_dataset(path, n, order="random", seed=42):
    """Input: destination, size, order, seed. Output: manifest dictionary.

    Every integer in [0,n) occurs exactly once. Random order is a seeded
    Fisher-Yates shuffle via random.shuffle, not a data-structure library.
    Generation, compression, and hashing are excluded from benchmark timing.
    """
    if type(n) is not int or not 1 <= n <= MAX_N:
        raise ValueError(f"n must be an integer between 1 and {MAX_N}")
    if order not in {"random", "ascending", "descending"}:
        raise ValueError("order must be random, ascending, or descending")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    values = array("I", range(n - 1, -1, -1) if order == "descending" else range(n))
    if values.itemsize != 4:
        raise RuntimeError("Dataset format requires a 32-bit unsigned I array")
    if order == "random":
        random.Random(seed).shuffle(values)
    if sys.byteorder != "little":
        values.byteswap()
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as stream:
        with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as compressed:
            view = memoryview(values).cast("B")
            for start in range(0, len(view), 1 << 20):
                compressed.write(view[start:start + (1 << 20)])
    temporary.replace(path)
    manifest = {
        "format": "gzip of little-endian uint32; no binary header",
        "n": n, "order": order, "seed": seed, "unique": True,
        "key_min": 0, "key_max": n - 1, "uncompressed_bytes": 4 * n,
        "compressed_bytes": path.stat().st_size, "sha256": sha256_file(path),
        "filename": path.name, "python_version": sys.version.split()[0],
        "generator": "array(I, range(n)) with seeded random.shuffle for random order",
    }
    path.with_suffix(path.suffix + ".json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def load_dataset(path, verify=True):
    """Input: dataset path and verification flag. Output: native-endian array.

    Verify its manifest hash and exact length; checksum checks detect file
    corruption, not whether an arbitrary external file is a permutation.
    """
    path = Path(path)
    manifest = json.loads(path.with_suffix(path.suffix + ".json").read_text())
    if verify and sha256_file(path) != manifest["sha256"]:
        raise ValueError("Dataset checksum does not match its manifest")
    values = array("I")
    if values.itemsize != 4:
        raise RuntimeError("Dataset format requires 32-bit I arrays")
    with gzip.open(path, "rb") as stream:
        while chunk := stream.read(1 << 20):
            if len(chunk) % 4:
                raise ValueError("Dataset has a truncated uint32 value")
            values.frombytes(chunk)
    if len(values) != manifest["n"]:
        raise ValueError("Dataset length does not match its manifest")
    if sys.byteorder != "little":
        values.byteswap()
    return values


def ensure_dataset(directory, n, order, seed):
    """Input: generation parameters. Output: path, generating only if absent."""
    path = dataset_path(directory, n, order, seed)
    if not path.exists() or not path.with_suffix(path.suffix + ".json").exists():
        generate_dataset(path, n, order, seed)
    manifest = json.loads(path.with_suffix(path.suffix + ".json").read_text())
    if (manifest["n"], manifest["order"], manifest["seed"]) != (n, order, seed):
        raise ValueError("Existing dataset metadata differs from requested parameters")
    return path


def main():
    """Input: CLI arguments. Output: dataset files and a printed manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--order", choices=["random", "ascending", "descending"], default="random")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--directory", type=Path, default=Path("data"))
    args = parser.parse_args()
    path = dataset_path(args.directory, args.size, args.order, args.seed)
    print(json.dumps(generate_dataset(path, args.size, args.order, args.seed), indent=2))


if __name__ == "__main__":
    main()
