"""Scapegoat ordered set: partial rebuilding with alpha = 2/3.

Uses ordinary BST links and the packed storage from ``base.py``. Scapegoat
nodes need no height or subtree-size metadata.
"""

from array import array
import math

from .base import NULL, PackedBST


LOG_3_OVER_2 = math.log(1.5)


class ScapegoatTree(PackedBST):
    """Scapegoat BST: worst-case logarithmic search, amortized updates."""

    def __init__(self):
        """Input: none. Output: an empty Scapegoat Tree."""
        super().__init__()
        # q counts successful insertions since the last full rebuild, plus
        # the size at that rebuild. It is an upper bound on the live-node count.
        self.max_size = 0

    def _subtree_size(self, node):
        """Input: subtree root. Output: number of nodes in that subtree."""
        if node == NULL:
            return 0
        count = 0
        stack = [node]
        while stack:
            current = stack.pop()
            count += 1
            if self.left[current] != NULL:
                stack.append(self.left[current])
            if self.right[current] != NULL:
                stack.append(self.right[current])
        return count

    def _rebuild(self, node):
        """Input: subtree root. Output: none; rebuild it into balanced form.

        Reuses the existing node indices, preserving parent links and the
        surrounding tree. An iterative rebuild avoids Python recursion limits.
        """
        if node == NULL:
            return
        parent = self.parent[node]
        was_left = parent != NULL and self.left[parent] == node

        # Collect nodes in increasing key order, without copying their keys.
        ordered = array("i")
        stack = []
        current = node
        while stack or current != NULL:
            while current != NULL:
                stack.append(current)
                current = self.left[current]
            current = stack.pop()
            ordered.append(current)
            current = self.right[current]

        # Divide the sorted indices around each median (iterative recursion).
        pending = [(0, len(ordered), parent, was_left)]
        while pending:
            begin, end, parent, is_left = pending.pop()
            if begin >= end:
                continue
            middle = (begin + end) // 2
            current = ordered[middle]
            self.parent[current] = parent
            self.left[current] = NULL
            self.right[current] = NULL
            if parent == NULL:
                self.root = current
            elif is_left:
                self.left[parent] = current
            else:
                self.right[parent] = current
            pending.append((middle + 1, end, current, False))
            pending.append((begin, middle, current, True))

    def insert(self, key):
        """Input: integer key. Output: True if added, False if duplicate."""
        self._check_key(key)
        found, parent = self._find(key)
        if found != NULL:
            return False
        node = self._allocate(key, parent)
        if parent == NULL:
            self.root = node
        elif key < self.keys[parent]:
            self.left[parent] = node
        else:
            self.right[parent] = node
        self.max_size += 1

        depth = 0
        current = node
        while self.parent[current] != NULL:
            depth += 1
            current = self.parent[current]
        if depth <= math.log(self.max_size) / LOG_3_OVER_2 + 1e-12:
            return True

        # Find the first ancestor with a child occupying > 2/3 of its nodes.
        # Along this path the sibling subtrees are disjoint: calculating their
        # sizes costs O(size of the eventually rebuilt subtree) in total.
        child = node
        child_size = 1
        while self.parent[child] != NULL:
            parent = self.parent[child]
            sibling = self.right[parent] if self.left[parent] == child else self.left[parent]
            parent_size = 1 + child_size + self._subtree_size(sibling)
            if 3 * child_size > 2 * parent_size:
                self._rebuild(parent)
                return True
            child, child_size = parent, parent_size
        raise AssertionError("Insertion exceeded the height bound without a scapegoat")

    def delete(self, key):
        """Input: integer key. Output: True if removed, False if absent."""
        self._check_key(key)
        node, _ = self._find(key)
        if node == NULL:
            return False
        if self.left[node] != NULL and self.right[node] != NULL:
            successor = self.right[node]
            while self.left[successor] != NULL:
                successor = self.left[successor]
            self.keys[node] = self.keys[successor]
            node = successor
        child = self.left[node] if self.left[node] != NULL else self.right[node]
        self._replace(node, child)
        self._release(node)

        # Full rebuilding after enough deletions bounds height by O(log n).
        if 2 * self.size < self.max_size:
            if self.root != NULL:
                self._rebuild(self.root)
            self.max_size = self.size
        return True