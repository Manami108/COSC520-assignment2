# Synthetic ordered-set datasets

Files named `keys_N_ORDER_seedS.u32.gz` hold exactly N little-endian unsigned
32-bit integers, gzip-compressed, with no binary header. Every key in [0,N)
occurs exactly once. A `.u32.gz.json` file records count, seed, order, SHA-256 of
compressed bytes, compressed/uncompressed sizes, and generator information.

`random` is a seeded shuffle of that universe. `ascending` and `descending`
test structured insertion orders. Each dataset costs 4*N bytes uncompressed:
ten million keys occupy 40,000,000 bytes, about 38.15 MiB.

Generate or read a dataset from the project root:

```bash
python -m experiments.dataset --size 10000000 --order random --seed 42 --directory data
```

```python
from experiments.dataset import load_dataset
keys = load_dataset("data/keys_10000000_random_seed42.u32.gz")
print(len(keys), keys[:5])
```

The initial package includes a generated ten-million-key random dataset. Its
manifest is the authoritative checksum for those exact bytes. Other sizes are
created automatically when needed. The standard-library shuffle is seeded,
but bit-for-bit regeneration across every Python version is not promised;
share the actual saved dataset and manifest for exact reproducibility.

Gzip headers are deterministic (no timestamp/original filename), and hashing is
streaming. Loading checks the hash and exact count, but does not prove that a
modified external dataset is a permutation of [0,N). The benchmark correctness
checks assume this generator's universe; do not silently substitute arbitrary
data with a different membership distribution.

Binary datasets are excluded from normal Git commits. Upload the actual `.gz`
and `.json` as release assets or to a public dataset host, and include a working
download URL in your report. Keep the manifest with the dataset. No dataset has
been published publicly during creation of this package.
