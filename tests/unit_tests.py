"""Correctness tests for AVL, Treap, and Scapegoat ordered sets.

Run from the project root:
    python -m unittest discover -s tests -p 'test_*.py' -v

Python ``set`` and ``sorted`` are used only as independent test oracles.
The tree implementations must not use built-in balanced-tree libraries.
"""

import math
import random
import unittest

from structures import AVLTree, ScapegoatTree, Treap, TREE_TYPES, make_tree
from structures.base import MAX_KEY, MIN_KEY, NULL


class CommonTreeTests(unittest.TestCase):
    """All three structures must implement the same ordered-set behavior."""

    def check_contents(self, tree, expected):
        """Compare cardinality, sorted keys, and internal invariants."""
        self.assertEqual(len(tree), len(expected))
        self.assertEqual(list(tree.inorder()), sorted(expected))
        self.assertTrue(tree.validate())
        if expected:
            self.assertGreater(tree.height(), 0)
        else:
            self.assertEqual(tree.height(), 0)

    def test_registry_and_common_interface(self):
        """There must be exactly the three selected data structures."""
        self.assertEqual(set(TREE_TYPES), {"avl", "treap", "scapegoat"})
        for name in TREE_TYPES:
            with self.subTest(tree=name):
                tree = make_tree(name, seed=7)
                for method in ("insert", "contains", "delete", "inorder",
                               "height", "storage_bytes", "validate"):
                    self.assertTrue(callable(getattr(tree, method)))
                self.assertIsInstance(tree.storage_bytes(), int)
                self.assertGreater(tree.storage_bytes(), 0)

    def test_empty_and_single_node(self):
        """Check empty-tree behavior and deletion of the only node."""
        for name in TREE_TYPES:
            with self.subTest(tree=name):
                tree = make_tree(name)
                self.check_contents(tree, set())
                self.assertFalse(tree.contains(10))
                self.assertFalse(tree.delete(10))
                self.assertTrue(tree.insert(10))
                self.assertTrue(tree.contains(10))
                self.assertEqual(tree.height(), 1)
                self.check_contents(tree, {10})
                self.assertTrue(tree.delete(10))
                self.check_contents(tree, set())
                self.assertFalse(tree.delete(10))

    def test_duplicates_and_missing_keys(self):
        """Duplicate insertions and missing deletions must be no-ops."""
        for name in TREE_TYPES:
            with self.subTest(tree=name):
                tree = make_tree(name)
                for key in (10, 5, 15):
                    self.assertTrue(tree.insert(key))
                self.assertFalse(tree.insert(10))
                self.assertFalse(tree.insert(5))
                self.assertFalse(tree.contains(99))
                self.assertFalse(tree.delete(99))
                self.check_contents(tree, {5, 10, 15})

    def test_deletion_of_nodes_with_zero_one_or_two_children(self):
        """Delete a real leaf, one-child node, and two-child node in each tree."""
        insertion_order = list(range(80))
        random.Random(789).shuffle(insertion_order)
        for name in TREE_TYPES:
            for child_count in (0, 1, 2):
                with self.subTest(tree=name, children=child_count):
                    tree = make_tree(name)
                    for key in insertion_order:
                        tree.insert(key)
                    # Pick a node with this child count in the ACTUAL tree;
                    # rotations can change its shape after insertion.
                    matching = [node for node in range(len(tree.keys))
                                if int(tree.left[node] != NULL)
                                 + int(tree.right[node] != NULL) == child_count]
                    self.assertTrue(matching)
                    deleted = tree.keys[matching[0]]
                    self.assertTrue(tree.delete(deleted))
                    self.assertFalse(tree.contains(deleted))
                    self.check_contents(tree, set(insertion_order) - {deleted})
                    self.assertFalse(tree.delete(deleted))

    def test_delete_actual_root_repeatedly(self):
        """Root deletion must keep links valid regardless of tree shape."""
        for name in TREE_TYPES:
            with self.subTest(tree=name):
                tree = make_tree(name)
                for key in (8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7):
                    tree.insert(key)
                expected = set(tree.inorder())
                while expected:
                    root_key = tree.keys[tree.root]
                    self.assertIn(root_key, expected)
                    self.assertTrue(tree.delete(root_key))
                    expected.remove(root_key)
                    self.check_contents(tree, expected)

    def test_key_boundaries_and_rejected_types(self):
        """Allow signed 64-bit endpoints and reject invalid key types/values."""
        for name in TREE_TYPES:
            with self.subTest(tree=name):
                tree = make_tree(name)
                keys = (MIN_KEY, -1, 0, 1, MAX_KEY)
                for key in keys:
                    self.assertTrue(tree.insert(key))
                self.check_contents(tree, set(keys))
                for method in (tree.insert, tree.contains, tree.delete):
                    for invalid in (True, False, 1.5, "7", None):
                        with self.subTest(operation=method.__name__, value=invalid):
                            with self.assertRaises(TypeError):
                                method(invalid)
                    for invalid in (MIN_KEY - 1, MAX_KEY + 1):
                        with self.assertRaises(ValueError):
                            method(invalid)
                self.check_contents(tree, set(keys))

    def test_ascending_descending_and_random_insertion(self):
        """All insertion orders must yield the same set and valid invariants."""
        rng = random.Random(2026)
        random_order = list(range(1000))
        rng.shuffle(random_order)
        orders = (list(range(1000)), list(range(999, -1, -1)), random_order)
        for name in TREE_TYPES:
            for order_index, values in enumerate(orders):
                with self.subTest(tree=name, order=order_index):
                    tree = make_tree(name, seed=42)
                    for value in values:
                        self.assertTrue(tree.insert(value))
                    self.check_contents(tree, set(values))
                    for key in (0, 1, 500, 999):
                        self.assertTrue(tree.contains(key))
                    self.assertFalse(tree.contains(1000))

    def test_randomized_operations_match_python_set(self):
        """Compare mixed inserts, searches, and deletes with an independent oracle."""
        for name in TREE_TYPES:
            for seed in range(5):
                with self.subTest(tree=name, seed=seed):
                    rng = random.Random(seed)
                    tree = make_tree(name, seed=seed)
                    expected = set()
                    for step in range(750):
                        key = rng.randrange(-200, 201)
                        operation = rng.randrange(3)
                        if operation == 0:
                            result = tree.insert(key)
                            self.assertEqual(result, key not in expected)
                            expected.add(key)
                        elif operation == 1:
                            result = tree.delete(key)
                            self.assertEqual(result, key in expected)
                            expected.discard(key)
                        else:
                            self.assertEqual(tree.contains(key), key in expected)
                        self.assertEqual(len(tree), len(expected))
                        if step % 50 == 0:
                            self.check_contents(tree, expected)
                    self.check_contents(tree, expected)

    def test_deleted_storage_slots_are_reused(self):
        """Repeated delete/reinsert cycles should not grow node arrays without limit."""
        for name in TREE_TYPES:
            with self.subTest(tree=name):
                tree = make_tree(name)
                for cycle in range(4):
                    keys = list(range(100 * cycle, 100 * (cycle + 1)))
                    for key in keys:
                        tree.insert(key)
                    self.assertEqual(len(tree.keys), 100)
                    self.check_contents(tree, set(keys))
                    for key in keys:
                        self.assertTrue(tree.delete(key))
                    self.check_contents(tree, set())
                self.assertEqual(len(tree.keys), 100)

    def test_validator_detects_broken_parent_link(self):
        """Invariant checks should reject a deliberately damaged tree."""
        for name in TREE_TYPES:
            with self.subTest(tree=name):
                tree = make_tree(name)
                for key in (20, 10, 30):
                    tree.insert(key)
                root = tree.root
                child = tree.left[root] if tree.left[root] != NULL else tree.right[root]
                self.assertNotEqual(child, NULL)
                previous_parent = tree.parent[child]
                tree.parent[child] = NULL
                try:
                    with self.assertRaises(AssertionError):
                        tree.validate()
                finally:
                    tree.parent[child] = previous_parent
                self.assertTrue(tree.validate())


class AVLTests(unittest.TestCase):
    """AVL-specific height maintenance and rotation checks."""

    def test_four_insertion_rotation_patterns(self):
        """LL, RR, LR, and RL should each produce root key 20."""
        for values in ((30, 20, 10), (10, 20, 30),
                       (30, 10, 20), (10, 30, 20)):
            with self.subTest(order=values):
                tree = AVLTree()
                for value in values:
                    tree.insert(value)
                self.assertEqual(tree.keys[tree.root], 20)
                self.assertEqual(tree.height(), 2)
                self.assertTrue(tree.validate())

    def test_deletion_rebalances(self):
        """Deletion may need rotations even when insertion already balanced."""
        for values, removed in (([4, 2, 5, 1, 3], 5),
                                ([2, 1, 4, 3, 5], 1)):
            with self.subTest(removed=removed):
                tree = AVLTree()
                for value in values:
                    tree.insert(value)
                self.assertTrue(tree.delete(removed))
                self.assertTrue(tree.validate())
                self.assertEqual(list(tree.inorder()), sorted(set(values) - {removed}))

    def test_large_sorted_sequence_remains_short(self):
        """AVL height stays logarithmic after monotonically ordered insertions."""
        tree = AVLTree()
        for value in range(2000):
            tree.insert(value)
        self.assertLessEqual(tree.height(), 2 * math.ceil(math.log2(2001)))
        self.assertTrue(tree.validate())


class TreapTests(unittest.TestCase):
    """Treap-specific reproducibility and heap-order checks."""

    def test_identical_seed_reproduces_shape_and_priorities(self):
        """With fixed insertion order and seed, the Treap should be reproducible."""
        trees = (Treap(seed=17), Treap(seed=17))
        for tree in trees:
            for key in (30, 10, 50, 5, 20, 40, 60, 15):
                tree.insert(key)
            self.assertTrue(tree.validate())
        self.assertEqual(trees[0].keys, trees[1].keys)
        self.assertEqual(trees[0].meta, trees[1].meta)
        self.assertEqual(trees[0].left, trees[1].left)
        self.assertEqual(trees[0].right, trees[1].right)

    def test_equal_priorities_are_tie_broken_by_key(self):
        """Forced priority collisions must preserve the Treap heap order."""
        class ConstantPriority:
            def getrandbits(self, count):
                return 7

        tree = Treap(seed=1)
        tree.rng = ConstantPriority()
        for key in (5, 3, 7, 1, 4, 6, 9):
            tree.insert(key)
        self.assertTrue(tree.validate())
        for key in (5, 1, 9, 3, 7, 4, 6):
            self.assertTrue(tree.delete(key))
            self.assertTrue(tree.validate())
        self.assertEqual(len(tree), 0)


class ScapegoatTests(unittest.TestCase):
    """Scapegoat rebuilding and historical-size threshold checks."""

    def test_ordered_insertions_trigger_partial_rebuilding(self):
        """Sorted insertions should force rebuilding and prevent a long chain."""
        tree = ScapegoatTree()
        rebuild_sizes = []
        original_rebuild = tree._rebuild

        def record_rebuild(node):
            rebuild_sizes.append(tree._subtree_size(node))
            original_rebuild(node)

        tree._rebuild = record_rebuild
        for key in range(300):
            self.assertTrue(tree.insert(key))
        self.assertGreater(len(rebuild_sizes), 0)
        self.assertLess(tree.height(), 50)
        self.assertEqual(tree.max_size, len(tree))
        self.assertTrue(tree.validate())

    def test_deletion_triggers_full_rebuild_and_resets_max_size(self):
        """Deleting over half the nodes triggers full rebuilding."""
        tree = ScapegoatTree()
        for key in range(31):
            tree.insert(key)
        self.assertEqual(tree.max_size, 31)
        for key in range(16):
            self.assertTrue(tree.delete(key))
        self.assertEqual(len(tree), 15)
        self.assertEqual(tree.max_size, 15)
        self.assertEqual(list(tree.inorder()), list(range(16, 31)))
        self.assertTrue(tree.validate())
        for key in range(16, 31):
            self.assertTrue(tree.delete(key))
        self.assertEqual(tree.max_size, 0)
        self.assertTrue(tree.validate())

    def test_rebuild_keeps_all_keys_and_links(self):
        """Deletion and further insertion must preserve node links after rebuild."""
        tree = ScapegoatTree()
        for key in range(600):
            tree.insert(key)
        for key in range(0, 600, 2):
            self.assertTrue(tree.delete(key))
        for key in range(600, 900):
            self.assertTrue(tree.insert(key))
        expected = set(range(1, 600, 2)) | set(range(600, 900))
        self.assertEqual(list(tree.inorder()), sorted(expected))
        self.assertTrue(tree.validate())


if __name__ == "__main__":
    unittest.main()
