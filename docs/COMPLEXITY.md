# Complexity notes for preparing your own report

These are AI-generated explanatory notes, not a completed report. Explain the
reasoning in your own words and cite the primary sources in REFERENCES.md.

Let n be the current live-key count, h the current tree height, q the number of
queries, u the number of updates, and a the number of allocated array slots.
Logs can be written log(n+1) to include the empty set.

| Structure | Search | Insert | Delete | Live-node space |
| --- | --- | --- | --- | --- |
| AVL | O(log(n+1)) worst case | O(log(n+1)) worst case | O(log(n+1)) worst case | O(n) |
| Randomized treap | O(log(n+1)) expected, O(n) worst case | Same | Same | O(n) |
| Splay | O(log(n+1)) amortized, O(n) single-operation worst case | Same | Same | O(n) |

Array append/pop and dynamic capacity expansion use amortized constant-cost
storage primitives. Thus these are tree-algorithm bounds in the standard model;
an individual Python array reallocation can copy its buffer. Packed implementation
storage is O(a), plus a free-slot array, and a may exceed n after many deletions.

## AVL

The invariant is abs(height(left)-height(right)) <= 1. Empty height is zero;
leaf height is one. The minimum node count obeys

```
N(0)=0; N(1)=1; N(h)=1+N(h-1)+N(h-2)=F(h+2)-1.
```

Fibonacci growth is exponential in h, giving h=O(log(n+1)). Finding a key walks
one root-to-leaf path. Updates walk ancestors, recomputing heights and applying
constant-size rotations. Therefore O(h) work gives the bounds in the table.
Building n keys by repeated insertion takes O(n log(n+1)) total worst-case tree
work. This implementation updates the whole ancestor path even if the height
stops changing; it does not use an early-stop optimization.

## Treap

Keys follow BST order; independent random priorities impose heap order. With
ideal distinct random priorities the induced shape is distributed like a BST
from random insertion order. Harmonic expected search-path lengths give
O(log(n+1)) expected depth; finding and restoring the heap costs expected O(log n).
Bad priority orders can create a chain and O(n) operations.

The implementation uses a seeded pseudorandom generator with 64-bit priorities
and key tie-breaking. Finite priority collisions are possible; the classical
bound assumes ideal random priorities. At ten million keys the birthday union
bound for at least one collision is roughly n(n-1)/(2*2^64), about 2.7e-6.
Repeated insertion construction is O(n log(n+1)) expected. Fixed seeds make a
run reproducible; expectation is over the priority randomness, not a guarantee
that every seed is fast.

## Splay

A single root-to-node access can cost O(n). Splaying changes the structure with
zig, zig-zig, and zig-zag rotations. The access lemma uses the potential
sum over nodes of log(subtree size). Potential changes pay for expensive calls,
yielding O(log(n+1)) amortized search/insertion/deletion over operation sequences.
The implementation does not store subtree sizes; they belong to the analysis.

Repeated insertion from empty is O(n log(n+1)) total amortized upper-bound work,
but ascending insertion in this implementation is linear: each new maximum is
attached near the root and rotated once. This does not contradict the upper
bound. A legal deep chain can still remain. A sequence of q queries plus u
updates is analyzed using its full history; do not claim each measured splay
call has worst-case logarithmic cost. For an arbitrary pre-existing shape,
potential at the start also matters when bounding the time of a short batch.

## Other public methods

`inorder()` takes O(n) total time and O(h) auxiliary stack space. The structural
debug validators take O(a+n) time/space because they check free-slot accounting
and metadata. `storage_bytes()` checks a constant number of array headers and
does not traverse nodes. Diagnostic validation is outside benchmark timing.
