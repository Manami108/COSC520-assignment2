"""Differential tests use Python set ONLY as an untimed correctness oracle."""

import random
import unittest

from structures import AVLTree, SplayTree, Treap, TREE_TYPES, make_tree
from structures.base import MAX_KEY, MIN_KEY, NULL


class OrderedSetTests(unittest.TestCase):
    """Exercise public behavior and structural invariants for every tree."""

    def test_empty_duplicates_boundaries_and_root_deletion(self):
        """Verify edge keys, duplicates, failed operations, and empty transitions."""
        for name in TREE_TYPES:
            with self.subTest(tree=name):
                tree = make_tree(name)
                self.assertFalse(tree.contains(0))
                self.assertFalse(tree.delete(0))
                for key in (0, MIN_KEY, MAX_KEY, -1, 1):
                    self.assertTrue(tree.insert(key))
                    self.assertFalse(tree.insert(key))
                    tree.validate()
                self.assertEqual(list(tree.inorder()), [MIN_KEY, -1, 0, 1, MAX_KEY])
                while len(tree):
                    self.assertTrue(tree.delete(tree.keys[tree.root]))
                    tree.validate()
                self.assertEqual(tree.root, NULL)

    def test_invalid_inputs_leave_tree_unchanged(self):
        """Reject non-integers and overflow before any mutation."""
        for name in TREE_TYPES:
            tree = make_tree(name)
            tree.insert(1)
            for method in (tree.insert, tree.contains, tree.delete):
                for value in (True, 1.2, "1", None):
                    with self.assertRaises(TypeError):
                        method(value)
                for value in (MIN_KEY - 1, MAX_KEY + 1):
                    with self.assertRaises(ValueError):
                        method(value)
            self.assertEqual(list(tree.inorder()), [1])
            tree.validate()

    def test_differential_random_operation_sequences(self):
        """Compare mixed operations to set and independently validate tree shape."""
        for name in TREE_TYPES:
            for seed in range(20):
                with self.subTest(tree=name, seed=seed):
                    rng, tree, oracle = random.Random(seed), make_tree(name, seed), set()
                    for step in range(600):
                        key = rng.randrange(-150, 151)
                        operation = rng.randrange(3)
                        if operation == 0:
                            self.assertEqual(tree.insert(key), key not in oracle)
                            oracle.add(key)
                        elif operation == 1:
                            self.assertEqual(tree.delete(key), key in oracle)
                            oracle.discard(key)
                        else:
                            self.assertEqual(tree.contains(key), key in oracle)
                        self.assertEqual(len(tree), len(oracle))
                        if step % 17 == 0:
                            self.assertEqual(list(tree.inorder()), sorted(oracle))
                            tree.validate()
                    tree.validate()

    def test_slot_reuse_does_not_grow_storage_forever(self):
        """Repeated full deletion/reinsertion must recycle allocated indices."""
        for name in TREE_TYPES:
            tree = make_tree(name)
            for cycle in range(5):
                keys = list(range(100 * cycle, 100 * (cycle + 1)))
                for key in keys:
                    tree.insert(key)
                self.assertEqual(len(tree.keys), 100)
                tree.validate()
                for key in keys:
                    self.assertTrue(tree.delete(key))
                tree.validate()

    def test_avl_four_rotation_cases(self):
        """LL, RR, LR, and RL insertions should produce the same balanced root."""
        for sequence in ((30, 20, 10), (10, 20, 30), (30, 10, 20), (10, 30, 20)):
            tree = AVLTree()
            for key in sequence:
                tree.insert(key)
                tree.validate()
            self.assertEqual(tree.keys[tree.root], 20)

    def test_avl_deletion_rebalances_with_zero_balance_child(self):
        """Cover deletion cases that differ from insertion rotation conditions."""
        for keys, deleted in (([4, 2, 5, 1, 3], 5), ([2, 1, 4, 3, 5], 1)):
            tree = AVLTree()
            for key in keys:
                tree.insert(key)
            self.assertTrue(tree.delete(deleted))
            tree.validate()
            self.assertEqual(list(tree.inorder()), sorted(set(keys) - {deleted}))

    def test_splay_success_miss_and_duplicate_move_expected_node(self):
        """Check the access behavior beyond ordinary membership correctness."""
        tree = SplayTree()
        for key in (10, 20, 30, 40):
            tree.insert(key)
            self.assertEqual(tree.keys[tree.root], key)
        self.assertTrue(tree.contains(20))
        self.assertEqual(tree.keys[tree.root], 20)
        _, last = tree._find(25)
        last_key = tree.keys[last]
        self.assertFalse(tree.contains(25))
        self.assertEqual(tree.keys[tree.root], last_key)
        self.assertFalse(tree.insert(10))
        self.assertEqual(tree.keys[tree.root], 10)
        self.assertFalse(tree.delete(99))
        self.assertEqual(tree.keys[tree.root], 40)
        tree.validate()

    def test_splay_deep_chain_has_no_recursion_limit(self):
        """A sorted build creates a deep splay chain; access/delete still works."""
        tree = SplayTree()
        for key in range(20000):
            tree.insert(key)
        tree.validate()
        self.assertTrue(tree.contains(0))
        self.assertEqual(tree.keys[tree.root], 0)
        for key in (0, 19999, 10000):
            self.assertTrue(tree.delete(key))
        tree.validate()

    def test_treap_seed_reproducibility(self):
        """The same seed/input reproduces key links and random priorities."""
        trees = [Treap(seed=77), Treap(seed=77)]
        for tree in trees:
            for key in (4, 2, 8, 1, 3, 6, 9):
                tree.insert(key)
            tree.validate()
        self.assertEqual(trees[0].meta, trees[1].meta)
        self.assertEqual(trees[0].left, trees[1].left)
        self.assertEqual(trees[0].right, trees[1].right)

    def test_treap_priority_ties_use_key_order(self):
        """Artificial collisions must keep deterministic, valid heap ordering."""
        class TiedRandom:
            def getrandbits(self, bits):
                """Input: requested bits. Output: fixed priority to force ties."""
                return 7
        tree = Treap()
        tree.rng = TiedRandom()
        for key in (5, 3, 7, 1, 4, 6, 9):
            tree.insert(key)
            tree.validate()
        for key in (5, 1, 9, 3, 7, 4, 6):
            self.assertTrue(tree.delete(key))
            tree.validate()


if __name__ == "__main__":
    unittest.main()
