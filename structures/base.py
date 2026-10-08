"""Hand-written, iterative binary-search-tree primitives over packed arrays.

AI-generated reference code; see docs/AI_USAGE.md before academic submission.
Arrays store raw values, not a library implementation of any tree algorithm.
"""

from array import array
import sys

NULL = -1
MIN_KEY = -(1 << 63)
MAX_KEY = (1 << 63) - 1


class PackedBST:
    """Common storage and rotations; subclasses provide balancing policies."""

    def __init__(self, metadata_type=None):
        """Input: optional array type. Output: an empty integer-key tree."""
        self.keys = array("q")
        self.left = array("i")
        self.right = array("i")
        self.parent = array("i")
        if self.keys.itemsize != 8 or self.left.itemsize != 4:
            raise RuntimeError("This implementation requires 64-bit q and 32-bit i arrays")
        self.meta = array(metadata_type) if metadata_type else None
        self.free = array("i")
        self.root = NULL
        self.size = 0

    def __len__(self):
        """Input: none. Output: the number of live, distinct keys."""
        return self.size

    @staticmethod
    def _check_key(key):
        """Input: a key. Output: none; reject keys outside signed 64-bit integers."""
        if type(key) is not int:
            raise TypeError("Keys must be Python integers (not bool or float)")
        if not MIN_KEY <= key <= MAX_KEY:
            raise ValueError("Key is outside the signed 64-bit range")

    def _allocate(self, key, parent=NULL, metadata=0):
        """Input: key, parent, metadata. Output: index of a new or reused slot."""
        if self.free:
            node = self.free.pop()
            self.keys[node] = key
            self.left[node] = self.right[node] = NULL
            self.parent[node] = parent
            if self.meta is not None:
                self.meta[node] = metadata
        else:
            node = len(self.keys)
            if node >= (1 << 31) - 1:
                raise OverflowError("The signed 32-bit node-index limit was reached")
            self.keys.append(key)
            self.left.append(NULL)
            self.right.append(NULL)
            self.parent.append(parent)
            if self.meta is not None:
                self.meta.append(metadata)
        self.size += 1
        return node

    def _release(self, node):
        """Input: a disconnected node. Output: none; recycle its storage slot."""
        self.left[node] = self.right[node] = self.parent[node] = NULL
        self.free.append(node)
        self.size -= 1

    def _find(self, key):
        """Input: a valid key. Output: matching node and last node visited."""
        node, last = self.root, NULL
        while node != NULL:
            last = node
            value = self.keys[node]
            if key == value:
                return node, last
            node = self.left[node] if key < value else self.right[node]
        return NULL, last

    def contains(self, key):
        """Input: integer key. Output: whether it exists, without restructuring."""
        self._check_key(key)
        return self._find(key)[0] != NULL

    def _replace(self, old, new):
        """Input: subtree roots. Output: none; replace old's link with new."""
        parent = self.parent[old]
        if parent == NULL:
            self.root = new
        elif self.left[parent] == old:
            self.left[parent] = new
        else:
            self.right[parent] = new
        if new != NULL:
            self.parent[new] = parent

    def _rotate_left(self, node):
        """Input: node with right child. Output: root of the rotated subtree."""
        child = self.right[node]
        middle = self.left[child]
        self._replace(node, child)
        self.left[child] = node
        self.parent[node] = child
        self.right[node] = middle
        if middle != NULL:
            self.parent[middle] = node
        return child

    def _rotate_right(self, node):
        """Input: node with left child. Output: root of the rotated subtree."""
        child = self.left[node]
        middle = self.right[child]
        self._replace(node, child)
        self.right[child] = node
        self.parent[node] = child
        self.left[node] = middle
        if middle != NULL:
            self.parent[middle] = node
        return child

    def inorder(self):
        """Input: none. Output: lazy sorted keys; do not mutate while iterating."""
        stack, node = [], self.root
        while stack or node != NULL:
            while node != NULL:
                stack.append(node)
                node = self.left[node]
            node = stack.pop()
            yield self.keys[node]
            node = self.right[node]

    def storage_bytes(self):
        """Input: none. Output: allocated array bytes including array headers.

        Includes spare capacity and recycled slots, but excludes process memory,
        temporary stacks, the instance, and the treap random-generator object.
        """
        arrays = [self.keys, self.left, self.right, self.parent, self.free]
        if self.meta is not None:
            arrays.append(self.meta)
        return sum(sys.getsizeof(values) for values in arrays)

    def validate(self):
        """Input: none. Output: True; raise AssertionError on structural faults.

        This O(n) debug check is outside benchmark timing and uses O(n) memory.
        """
        assert (self.root == NULL) == (self.size == 0), "Root/size mismatch"
        if self.root != NULL:
            assert self.parent[self.root] == NULL, "Root has a parent"
        seen, stack = set(), [(self.root, None, None)]
        while stack:
            node, low, high = stack.pop()
            if node == NULL:
                continue
            assert 0 <= node < len(self.keys), "Invalid node index"
            assert node not in seen, "Cycle or repeated child"
            seen.add(node)
            key = self.keys[node]
            assert low is None or low < key, "BST lower bound violated"
            assert high is None or key < high, "BST upper bound violated"
            for child in (self.left[node], self.right[node]):
                if child != NULL:
                    assert self.parent[child] == node, "Parent link mismatch"
            stack.append((self.left[node], low, key))
            stack.append((self.right[node], key, high))
        assert len(seen) == self.size, "Unreachable live nodes"
        free = set(self.free)
        assert len(free) == len(self.free), "Duplicate free slots"
        assert not seen & free, "A free slot is still reachable"
        assert seen | free == set(range(len(self.keys))), "Lost storage slots"
        return True
