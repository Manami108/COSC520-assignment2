"""Randomized treap with BST key order and min-heap priority order."""

import random
from .base import NULL, PackedBST


class Treap(PackedBST):
    """Random priorities give expected O(log n) search, insertion, and deletion."""

    def __init__(self, seed=42):
        """Input: random seed. Output: an empty reproducible treap."""
        super().__init__("Q")
        self.rng = random.Random(seed)

    def _rank(self, node):
        """Input: node. Output: (priority, key); keys break rare priority ties."""
        return self.meta[node], self.keys[node]

    def insert(self, key):
        """Input: integer key. Output: True if added, False for a duplicate."""
        self._check_key(key)
        found, parent = self._find(key)
        if found != NULL:
            return False
        node = self._allocate(key, parent, self.rng.getrandbits(64))
        if parent == NULL:
            self.root = node
        elif key < self.keys[parent]:
            self.left[parent] = node
        else:
            self.right[parent] = node
        while self.parent[node] != NULL:
            parent = self.parent[node]
            if self._rank(parent) <= self._rank(node):
                break
            if self.left[parent] == node:
                self._rotate_right(parent)
            else:
                self._rotate_left(parent)
        return True

    def delete(self, key):
        """Input: integer key. Output: removal success; rotate target downward."""
        self._check_key(key)
        node, _ = self._find(key)
        if node == NULL:
            return False
        # Rotate the lower-priority child upward until the node has <=1 child.
        while self.left[node] != NULL and self.right[node] != NULL:
            if self._rank(self.left[node]) < self._rank(self.right[node]):
                self._rotate_right(node)
            else:
                self._rotate_left(node)
        child = self.left[node] if self.left[node] != NULL else self.right[node]
        self._replace(node, child)
        self._release(node)
        return True

    def validate(self):
        """Input: none. Output: True; verify BST and min-heap invariants."""
        super().validate()
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node == NULL:
                continue
            for child in (self.left[node], self.right[node]):
                if child != NULL:
                    assert self._rank(node) <= self._rank(child), "Priority heap violated"
                    stack.append(child)
        return True
