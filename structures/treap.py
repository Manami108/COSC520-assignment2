# A Treap combines the BST property for keys with the min-heap property for randomly assigned priorities. 
# Rotations restore the heap property after insertion and deletion.
import random
from .base import NULL, PackedBST

class Treap(PackedBST):
    def __init__(self, seed=42):
        # Input: random seed
        # Output: an empty reproducible treap
        super().__init__("Q")
        self.rng = random.Random(seed)

    def _rank(self, node):
        # Input: node
        # Output: (priority, key)
        # It uses the key to break ties between equal priorities
        return self.meta[node], self.keys[node]

    def insert(self, key):
        # Input: integer key
        # Output: True if added and false for a duplicate
        self._check_key(key)
        found, parent = self._find(key)
        if found != NULL:
            return False
        # The code assigns a random 64-bit priority to the new
        node = self._allocate(key, parent, self.rng.getrandbits(64))
        if parent == NULL:
            self.root = node
        elif key < self.keys[parent]:
            self.left[parent] = node
        else:
            self.right[parent] = node
        
        # The code restores the min-heap property (rank(parent) <= rank(child))
        # It rotates the new node upward until the heap property holds
        while self.parent[node] != NULL:
            parent = self.parent[node]
            if self._rank(parent) <= self._rank(node):
                break
            if self.left[parent] == node:
                # Right rotation
                self._rotate_right(parent)
            else:
                # Left rotation
                self._rotate_left(parent)
        return True

    def delete(self, key):
        # Input: integer key
        # Output: removal success
        self._check_key(key)
        node, _ = self._find(key)
        if node == NULL:
            return False
        # The code is to rotate the lower-priority child upward until the node has at most one child 
        while self.left[node] != NULL and self.right[node] != NULL:
            if self._rank(self.left[node]) < self._rank(self.right[node]):
                # Right rotation
                self._rotate_right(node)
            else:
                # Left rotation
                self._rotate_left(node)
        # this code removes the node and reconnects its remaining child
        child = self.left[node] if self.left[node] != NULL else self.right[node]
        self._replace(node, child)
        self._release(node)
        return True