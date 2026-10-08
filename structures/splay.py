"""Bottom-up splay tree with explicit zig, zig-zig, and zig-zag cases."""

from .base import NULL, PackedBST


class SplayTree(PackedBST):
    """Amortized O(log n) operations; an individual operation can take O(n)."""

    def __init__(self):
        """Input: none. Output: an empty tree without balancing metadata."""
        super().__init__()

    def _splay(self, node):
        """Input: live node. Output: none; move it to the root by rotations."""
        while self.parent[node] != NULL:
            parent = self.parent[node]
            grand = self.parent[parent]
            if grand == NULL:
                if self.left[parent] == node:
                    self._rotate_right(parent)
                else:
                    self._rotate_left(parent)
            elif self.left[grand] == parent and self.left[parent] == node:
                self._rotate_right(grand)
                self._rotate_right(parent)
            elif self.right[grand] == parent and self.right[parent] == node:
                self._rotate_left(grand)
                self._rotate_left(parent)
            elif self.left[grand] == parent:
                self._rotate_left(parent)
                self._rotate_right(grand)
            else:
                self._rotate_right(parent)
                self._rotate_left(grand)

    def contains(self, key):
        """Input: integer key. Output: membership; splay match or last visit."""
        self._check_key(key)
        found, last = self._find(key)
        if last != NULL:
            self._splay(last)
        return found != NULL

    def insert(self, key):
        """Input: integer key. Output: addition success; splay new/existing key."""
        self._check_key(key)
        found, parent = self._find(key)
        if found != NULL:
            self._splay(found)
            return False
        node = self._allocate(key, parent)
        if parent == NULL:
            self.root = node
        elif key < self.keys[parent]:
            self.left[parent] = node
        else:
            self.right[parent] = node
        self._splay(node)
        return True

    def delete(self, key):
        """Input: integer key. Output: removal success; join the two subtrees."""
        if not self.contains(key):
            return False
        node = self.root
        left, right = self.left[node], self.right[node]
        if left != NULL:
            self.parent[left] = NULL
        if right != NULL:
            self.parent[right] = NULL
        self._release(node)
        if left == NULL:
            self.root = right
            return True
        self.root = left
        maximum = left
        while self.right[maximum] != NULL:
            maximum = self.right[maximum]
        self._splay(maximum)
        self.right[self.root] = right
        if right != NULL:
            self.parent[right] = self.root
        return True
