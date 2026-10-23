# The code imports the three tree implementations
from .avl import AVLTree
from .treap import Treap
from .scapegoat import ScapegoatTree

TREE_TYPES = {"avl": AVLTree, "treap": Treap, "scapegoat": ScapegoatTree,}

def make_tree(name, seed=42):
    cls = TREE_TYPES[name]
    return cls(seed=seed) if name == "treap" else cls()