# Unit tests for AVL, Treap, and Scapegoat trees
import math
import random
import unittest

from structures import AVLTree, Treap, ScapegoatTree, TREE_TYPES, make_tree
from structures.base import NULL, MIN_KEY, MAX_KEY

class TreeTests(unittest.TestCase):
    def check(self, tree, expected):
        # Input: tree and expected set of keys
        # Output: set of live node indices
        # this block checks live links and invariants before calling inorder and height
        self.assertEqual(len(tree), len(expected))
        self.assertEqual(tree.root == NULL, not expected)
        count = len(tree.keys)
        self.assertEqual(len(tree.left), count)
        self.assertEqual(len(tree.right), count)
        self.assertEqual(len(tree.parent), count)
        
        # Each key has to satisfy lower bound < key < upper bound
        seen, height = set(), 0
        stack = [(tree.root, None, None, NULL, 1)]
        while stack:
            node, low, high, parent, depth = stack.pop()
            if node == NULL:
                continue
            self.assertTrue(0 <= node < count, "Invalid node index")
            self.assertNotIn(node, seen, "Cycle or shared child")
            seen.add(node)
            self.assertEqual(tree.parent[node], parent, "Broken parent link")
            key = tree.keys[node]
            if low is not None:
                self.assertGreater(key, low)
            if high is not None:
                self.assertLess(key, high)
            height = max(height, depth)
            stack.append((tree.left[node], low, key, node, depth + 1))
            stack.append((tree.right[node], key, high, node, depth + 1))

        free = set(tree.free)
        self.assertEqual(len(seen), len(expected))
        self.assertEqual(len(free), len(tree.free))
        self.assertFalse(seen & free)
        self.assertEqual(seen | free, set(range(count)))
        self.assertEqual(list(tree.inorder()), sorted(expected))
        self.assertEqual(tree.height(), height)

        if isinstance(tree, AVLTree):
            self.avl(tree)
        elif isinstance(tree, Treap):
            self.treap(tree)
        elif isinstance(tree, ScapegoatTree):
            self.scapegoat(tree)
        return seen 

    def avl(self, tree):
        # Input: AVL Tree
        # Output: none
        # This block checks actual AVL heights and balance factors (|h(left) - h(right)| <= 1) and verifies stored heights (h(v) = 1 + max(h(left), h(right)))
        heights = {NULL: 0}
        stack = [(tree.root, False)]
        while stack:
            node, visited = stack.pop()
            if node == NULL:
                continue
            if not visited:
                stack.extend(((node, True), (tree.left[node], False),
                              (tree.right[node], False)))
                continue
            left, right = heights[tree.left[node]], heights[tree.right[node]]
            self.assertLessEqual(abs(left - right), 1)
            heights[node] = max(left, right) + 1
            self.assertEqual(tree.meta[node], heights[node])

    def treap(self, tree):
        # Input: Treap
        # Output: none
        # This block checks the Treap's min-heap priority rule (rank(parent) <= rank(child))
        # Rank is also compared
        stack = [tree.root]
        while stack:
            node = stack.pop()
            if node == NULL:
                continue
            for child in (tree.left[node], tree.right[node]):
                if child != NULL:
                    self.assertLessEqual(
                        (tree.meta[node], tree.keys[node]),
                        (tree.meta[child], tree.keys[child]),
                    )
                    stack.append(child)

    def scapegoat(self, tree):
        # Input: Scapegoat Tree
        # Output: none
        # this block checks the historical-size (n <= q <= 2n, where q is max_size) and logarithmic-depth bounds (height - 1 <= log_(3/2)(q)).
        if len(tree) == 0:
            self.assertEqual(tree.max_size, 0)
        else:
            self.assertLessEqual(len(tree), tree.max_size)
            self.assertLessEqual(tree.max_size, 2 * len(tree))
            self.assertLessEqual(
                tree.height() - 1,
                math.log(tree.max_size) / math.log(1.5) + 1e-9,
            )

    def test_empty(self):
        # This block checks the common interface and behavior of empty trees.
        self.assertEqual(set(TREE_TYPES), {"avl", "treap", "scapegoat"})
        for name in TREE_TYPES:
            with self.subTest(tree=name):
                tree = make_tree(name)
                for method in ("insert", "search", "delete", "inorder", "height", "storage_bytes"):
                    self.assertTrue(callable(getattr(tree, method)))
                self.assertFalse(tree.search(10))
                self.assertFalse(tree.delete(10))
                self.assertGreater(tree.storage_bytes(), 0)
                self.check(tree, set())

    def test_insert_search(self):
        # this block checks insertion, searching, duplicate keys, and missing keys.
        for name in TREE_TYPES:
            with self.subTest(tree=name):
                tree = make_tree(name)
                for key in (20, 10, 30, 5, 15):
                    self.assertTrue(tree.insert(key))
                self.assertFalse(tree.insert(10))
                self.assertTrue(tree.search(15))
                self.assertFalse(tree.search(99))
                self.assertFalse(tree.delete(99))
                self.check(tree, {5, 10, 15, 20, 30})

    def test_delete_cases(self):
        # This block checks deletion of nodes with zero, one, and two children.
        keys = list(range(80))
        random.Random(7).shuffle(keys)
        for name in TREE_TYPES:
            for children in (0, 1, 2):
                with self.subTest(tree=name, children=children):
                    tree = make_tree(name)
                    for key in keys:
                        tree.insert(key)
                    live = self.check(tree, set(keys))
                    node = next((i for i in sorted(live)
                                 if int(tree.left[i] != NULL) + int(tree.right[i] != NULL)
                                 == children), None)
                    self.assertIsNotNone(node, "No node with requested child count")
                    key = tree.keys[node]
                    self.assertTrue(tree.delete(key))
                    self.assertFalse(tree.search(key))
                    self.check(tree, set(keys) - {key})

    def test_delete_root(self):
        # Repeatedly delete the current root until empty.
        for name in TREE_TYPES:
            tree = make_tree(name)
            expected = set(range(30))
            for key in range(30):
                tree.insert(key)
            while expected:
                key = tree.keys[tree.root]
                self.assertTrue(tree.delete(key))
                expected.remove(key)
                self.check(tree, expected)

    def test_keys(self):
       # This block checks valid 64-bit boundary keys and rejects invalid inputs.
       # Valid range is -2^63 <= key <= 2^63 - 1
        for name in TREE_TYPES:
            tree = make_tree(name)
            expected = {MIN_KEY, -1, 0, MAX_KEY}
            for key in expected:
                self.assertTrue(tree.insert(key))
            for method in (tree.insert, tree.search, tree.delete):
                for key in (True, 1.5, "4", None):
                    with self.assertRaises(TypeError):
                        method(key)
                for key in (MIN_KEY - 1, MAX_KEY + 1):
                    with self.assertRaises(ValueError):
                        method(key)
            self.check(tree, expected)

    def test_orders(self):
        # This block checks ascending, descending, and random insertion orders.
        shuffled = list(range(600))
        random.Random(42).shuffle(shuffled)
        for name in TREE_TYPES:
            for label, order in (("ascending", range(600)),
                                 ("descending", range(599, -1, -1)),
                                 ("random", shuffled)):
                with self.subTest(tree=name, order=label):
                    tree = make_tree(name)
                    for key in order:
                        self.assertTrue(tree.insert(key))
                    self.check(tree, set(range(600)))

    def test_random(self):
        # This code check mixed operations against Python's set with fixed seeds.
        for name in TREE_TYPES:
            for seed in (11, 22, 33):
                with self.subTest(tree=name, seed=seed):
                    tree, expected = make_tree(name, seed=seed), set()
                    rng = random.Random(seed)
                    for step in range(1200):
                        key, action = rng.randrange(-300, 301), rng.randrange(3)
                        if action == 0:
                            self.assertEqual(tree.insert(key), key not in expected)
                            expected.add(key)
                        elif action == 1:
                            self.assertEqual(tree.delete(key), key in expected)
                            expected.discard(key)
                        else:
                            self.assertEqual(tree.search(key), key in expected)
                        if step % 75 == 0:
                            self.check(tree, expected)
                    self.check(tree, expected)

    def test_reuse(self):
        # this block checks that deleted node slots are reused during later insertions.
        # The allocated key array should remain at 100 slots
        for name in TREE_TYPES:
            tree = make_tree(name)
            for cycle in range(3):
                keys = range(100 * cycle, 100 * (cycle + 1))
                for key in keys:
                    self.assertTrue(tree.insert(key))
                self.assertEqual(len(tree.keys), 100)
                for key in keys:
                    self.assertTrue(tree.delete(key))
                self.check(tree, set())

    def test_avl_rotations(self):
        # This block checks LL, RR, LR, and RL rotations using different insertion orders.
        for order in ((30, 20, 10), (10, 20, 30),
                      (30, 10, 20), (10, 30, 20)):
            with self.subTest(order=order):
                tree = AVLTree()
                for key in order:
                    tree.insert(key)
                self.assertEqual(tree.keys[tree.root], 20)
                self.check(tree, {10, 20, 30})

    def test_avl_delete(self):
        # This block checks that AVL balance is restored after deletion
        # The balance factor must remain between -1 and 1.
        for order, removed in (([4, 2, 5, 1, 3], 5),
                               ([2, 1, 4, 3, 5], 1)):
            tree = AVLTree()
            for key in order:
                tree.insert(key)
            self.assertTrue(tree.delete(removed))
            self.check(tree, set(order) - {removed})

    def test_treap_seed(self):
        # This block checks that identical seeds and keys reproduce the same
        a, b = Treap(seed=23), Treap(seed=23)
        for tree in (a, b):
            for key in (30, 10, 40, 5, 15, 35):
                tree.insert(key)
            self.check(tree, {5, 10, 15, 30, 35, 40})
        self.assertEqual(a.meta, b.meta)
        self.assertEqual(a.left, b.left)
        self.assertEqual(a.right, b.right)

    def test_scapegoat_insert(self):
        # This block checks that sorted insertions trigger subtree rebuilding.
        tree = ScapegoatTree()
        rebuilds = 0
        original = tree._rebuild

        def count_rebuild(node):
            nonlocal rebuilds
            rebuilds += 1
            original(node)

        tree._rebuild = count_rebuild
        for key in range(500):
            self.assertTrue(tree.insert(key))
        self.assertGreater(rebuilds, 0)
        self.assertEqual(tree.max_size, 500)
        self.check(tree, set(range(500)))

    def test_scapegoat_delete(self):
        # This block checks the full rebuild condition (2n < q).
        tree = ScapegoatTree()
        for key in range(31):
            tree.insert(key)
        for key in range(15):
            self.assertTrue(tree.delete(key))
        self.assertEqual(tree.max_size, 31)  # No rebuild yet (n=16, q=31).
        self.assertTrue(tree.delete(15))
        self.assertEqual(len(tree), 15)
        self.assertEqual(tree.max_size, 15)
        self.check(tree, set(range(16, 31)))
        for key in range(16, 31):
            self.assertTrue(tree.delete(key))
        self.check(tree, set())

if __name__ == "__main__":
    unittest.main()
