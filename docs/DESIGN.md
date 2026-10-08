# Design and reading order

All files in the initial package are AI-generated reference material.

1. Read `experiments/demo.py` to see the common interface.
2. Read `structures/base.py` for storage, search, parent-link updates, and rotations.
3. Read `structures/avl.py` for height repair and four rotation cases.
4. Read `structures/treap.py` for randomized priorities and heap-restoring rotations.
5. Read `structures/splay.py` for zig, zig-zig, zig-zag, and subtree joining.
6. Read `experiments/workloads.py` for operation sequences and known answers.
7. Read `experiments/worker.py` for timing and verification boundaries.
8. Read `experiments/benchmark.py` for subprocess isolation and persistence.
9. Read the tests, then reproduce failures with deliberately broken rotations.

## Common arena

Node i is represented by key[i], left[i], right[i], and parent[i]. `-1` is the
null index. The root is an index. Key storage uses signed 64-bit integers;
links use signed 32-bit indices. This implementation checks the array widths
at runtime and limits indices below 2^31-1.

AVL adds a 32-bit height per slot. Treap adds a 64-bit random priority. Splay
needs no balancing metadata. A free-index array recycles removed slots.
Representing a node as an array position rather than a Python object keeps
millions of nodes practical, while the algorithms still explicitly implement
all searching, insertion, deletion, and balancing.

All algorithms are iterative. In particular, a splay tree can legally be a
chain after sorted insertion. Avoiding recursive tree traversal or deletion
prevents that chain from hitting Python's recursion limit.

## Why these structures can be compared

They provide the same ordered-set semantics and O(n) live-node storage, but use
different strategies: deterministic height balance, random priority balance,
and adjustment to access history. This gives both an asymptotic comparison and
a workload-sensitive experiment. It is a proposed selection, not instructor
approval or the student's personal reason for choosing the topic.

## Specific algorithm choices

- AVL deletes a two-child node by copying its successor key and removing the
  successor slot, then repairs ancestors. There are no public persistent node
  handles, so replacing a node's stored key does not break the public interface.
- Treap uses a min-heap on `(priority, key)` so rare equal priorities are handled
  deterministically. Its random generator has a per-tree seed.
- Splay moves a matched key, or the last visited node on a miss, to the root.
  Deletion splays the maximum of the detached left subtree before attaching the
  right subtree.
- `validate()` checks root/parent consistency, cycles, key order, reachability,
  free-slot accounting, and the applicable balancing metadata. Its own sets
  are debug aids, not a data-structure implementation used in benchmarks.
