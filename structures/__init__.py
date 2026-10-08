"""Three manually implemented ordered sets; no third-party tree libraries."""

from .avl import AVLTree
from .treap import Treap
from .splay import SplayTree

TREE_TYPES = {"avl": AVLTree, "treap": Treap, "splay": SplayTree}


def make_tree(name, seed=42):
    """Input: name and seed. Output: an empty tree; treaps use the seed."""
    cls = TREE_TYPES[name]
    return cls(seed=seed) if name == "treap" else cls()
