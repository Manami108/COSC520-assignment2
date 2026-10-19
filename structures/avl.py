"""AVL ordered set: explicit height maintenance and single/double rotations."""

from .base import NULL, PackedBST


class AVLTree(PackedBST):
    """Strict height balance gives worst-case O(log n) operations."""

    def __init__(self):
        """Input: none. Output: an empty AVL tree with packed height metadata."""
        super().__init__("i")

    def _height(self, node):
        """Input: node index. Output: height, using zero for an empty subtree."""
        return 0 if node == NULL else self.meta[node]

    def _update_height(self, node):
        """Input: live node. Output: none; recompute height from its children."""
        self.meta[node] = 1 + max(self._height(self.left[node]), self._height(self.right[node]))

    def _balance_factor(self, node):
        """Input: live node. Output: left height minus right height."""
        return self._height(self.left[node]) - self._height(self.right[node])

    def _rotate_left_avl(self, node):
        """Input: node. Output: new subtree root after rotation/height repair."""
        root = self._rotate_left(node)
        self._update_height(node)
        self._update_height(root)
        return root

    def _rotate_right_avl(self, node):
        """Input: node. Output: new subtree root after rotation/height repair."""
        root = self._rotate_right(node)
        self._update_height(node)
        self._update_height(root)
        return root

    def _rebalance(self, node):
        """Input: ancestor of a change. Output: none; repair up to the root."""
        while node != NULL:
            self._update_height(node)
            balance = self._balance_factor(node)
            if balance > 1:
                if self._balance_factor(self.left[node]) < 0:
                    self._rotate_left_avl(self.left[node])
                node = self._rotate_right_avl(node)
            elif balance < -1:
                if self._balance_factor(self.right[node]) > 0:
                    self._rotate_right_avl(self.right[node])
                node = self._rotate_left_avl(node)
            node = self.parent[node]

    def insert(self, key):
        """Input: integer key. Output: True if added, False for a duplicate."""
        self._check_key(key)
        found, parent = self._find(key)
        if found != NULL:
            return False
        node = self._allocate(key, parent, 1)
        if parent == NULL:
            self.root = node
        elif key < self.keys[parent]:
            self.left[parent] = node
        else:
            self.right[parent] = node
        self._rebalance(parent)
        return True

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
        parent = self.parent[node]
        child = self.left[node] if self.left[node] != NULL else self.right[node]
        self._replace(node, child)
        self._release(node)
        self._rebalance(parent)
        return True

    def validate(self):
        """Input: none. Output: True; verify BST, height, and AVL invariants."""
        super().validate()
        heights, stack = {}, [(self.root, False)]
        while stack:
            node, visited = stack.pop()
            if node == NULL:
                continue
            if not visited:
                stack.extend(((node, True), (self.left[node], False), (self.right[node], False)))
                continue
            left = heights.get(self.left[node], 0)
            right = heights.get(self.right[node], 0)
            assert abs(left - right) <= 1, "AVL balance violated"
            heights[node] = 1 + max(left, right)
            assert self.meta[node] == heights[node], "Stale height"
        return True
