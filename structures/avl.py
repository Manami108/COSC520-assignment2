# AVL Tree strictly maintain the balance using rotations to keep the height difference of each node within [-1, 1].
# Single rotations handle LL and RR cases, while double rotations
# handle LR and RL cases.
from .base import NULL, PackedBST

class AVLTree(PackedBST):
    def __init__(self):
        # Input: none
        # Output: an empty AVL tree with packed height metadata
        super().__init__("i")

    def _height(self, node):
        # Input: node index 
        # Output: height using 0 for an empty subtree
        return 0 if node == NULL else self.meta[node]

    def _update_height(self, node):
        # Input: live node
        # Output: none
        # the code computes height h(v) = 1 + max(h(left), h(right))
        self.meta[node] = 1 + max(self._height(self.left[node]), self._height(self.right[node]))

    def _balance_factor(self, node):
        # Input: live node 
        # Output: left height - right height
        return self._height(self.left[node]) - self._height(self.right[node])

    def _rotate_left_avl(self, node):
        # Input: node 
        # Output: new subtree root updated after rotation and height repair
        # BF(v) = h(left) - h(right), where |BF(v)| <= 1
        root = self._rotate_left(node)
        self._update_height(node)
        self._update_height(root)
        return root

    def _rotate_right_avl(self, node):
        # Input: node 
        # Output: new subtree root updated after rotation and height repair
        root = self._rotate_right(node)
        self._update_height(node)
        self._update_height(root)
        return root

    def _rebalance(self, node):
        # Input: ancestor of a change
        # Output: none
        # This code repairs up to the root
        while node != NULL:
            self._update_height(node)
            balance = self._balance_factor(node)
            if balance > 1:
                if self._balance_factor(self.left[node]) < 0:
                    # LR case
                    self._rotate_left_avl(self.left[node])
                # LL case
                node = self._rotate_right_avl(node)
            elif balance < -1:
                if self._balance_factor(self.right[node]) > 0:
                    # RL case
                    self._rotate_right_avl(self.right[node])
                node = self._rotate_left_avl(node)
            # RR case
            node = self.parent[node]

    def insert(self, key):
        # Input: integer key 
        # Output: True if added, and false for a duplicate
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
        # Input: integer key 
        # Output: True if removed and false if absent
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