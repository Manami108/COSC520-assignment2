# This code is the base for AVL, Treap, and Scapegoat. 
# The code maintains the BST property: left key < parent key < right key
#It uses packed arrays to store keys, child indices, and parent indices instead of creating separate node objects.

from array import array
import sys

# NULL is an empty node and keys use signed 64-bit integers.
NULL = -1
MIN_KEY = -(1 << 63)
MAX_KEY = (1 << 63) - 1


class PackedBST:
    def __init__(self, metadata_type=None):
        # Input: optional array type
        # Output: an empty integer-key tree
        # q stores 64-bit keys, and i stores node indices
        self.keys = array("q")
        self.left = array("i")
        self.right = array("i")
        self.parent = array("i")
        self.meta = array(metadata_type) if metadata_type else None
        self.free = array("i")
        self.root = NULL
        self.size = 0
        
    def __len__(self):
        # Input: none
        # Output: the number of live, distinct keys
        return self.size

    @staticmethod
    def _check_key(key):
        # Input: a key
        # Output: none 
        # The code rejects keys outside 64-bit integers
        if type(key) is not int:
            raise TypeError("Keys must be Python integers (not bool or float)")
        if not MIN_KEY <= key <= MAX_KEY:
            raise ValueError("Key is outside the signed 64-bit range")

    def _allocate(self, key, parent=NULL, metadata=0):
        # Input: key, parent, metadata
        # Output: index of a new or reused slot
        # The code reuses deleted slots before allocating additional storage
        if self.free:
            node = self.free.pop()
            self.keys[node] = key
            self.left[node] = self.right[node] = NULL
            self.parent[node] = parent
            if self.meta is not None:
                self.meta[node] = metadata
        else:
            node = len(self.keys)
            self.keys.append(key)
            self.left.append(NULL)
            self.right.append(NULL)
            self.parent.append(parent)
            if self.meta is not None:
                self.meta.append(metadata)
        self.size += 1
        return node

    def _release(self, node):
        # Input: a disconnected node
        # Output: none
        # The code markes the node's slot as available.
        self.left[node] = self.right[node] = self.parent[node] = NULL
        self.free.append(node)
        self.size -= 1

    def _find(self, key):
        # Input: a valid key
        # Output: matching node and last node visited
        # The code searchs in O(h) time.
        node, last = self.root, NULL
        while node != NULL:
            last = node
            value = self.keys[node]
            if key == value:
                return node, last
            node = self.left[node] if key < value else self.right[node]
        return NULL, last

    def search(self, key):
        # Input: integer key
        # Output: whether it exists without restructuring
        self._check_key(key)
        return self._find(key)[0] != NULL

    def _replace(self, old, new):
        # Input: subtree roots
        # Output: none
        # The code replaces old's link with new
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
        # Input: node with right child
        # Output: root of the rotated subtree
        # Left rotation
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
        # Input: node with left child
        # Output: root of the rotated subtree
        # Right rotation
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
        # Input: none
        # Output: lazy sorted keys
        stack, node = [], self.root
        while stack or node != NULL:
            while node != NULL:
                stack.append(node)
                node = self.left[node]
            node = stack.pop()
            yield self.keys[node]
            node = self.right[node]

    def height(self):
        # Input: none
        # Output: tree height in nodes (empty tree has height 0)
        # It finds the maximum root-to-leaf depth using iterative traversal.
        if self.root == NULL:
            return 0
        maximum = 0
        stack = [(self.root, 1)]
        while stack:
            node, depth = stack.pop()
            maximum = max(maximum, depth)
            if self.left[node] != NULL:
                stack.append((self.left[node], depth + 1))
            if self.right[node] != NULL:
                stack.append((self.right[node], depth + 1))
        return maximum

    def storage_bytes(self):
        # Input: none
        # Output: allocated array bytes including array headers
        # This code is to measure array memory
        arrays = [self.keys, self.left, self.right, self.parent, self.free]
        if self.meta is not None:
            arrays.append(self.meta)
        return sum(sys.getsizeof(values) for values in arrays)
