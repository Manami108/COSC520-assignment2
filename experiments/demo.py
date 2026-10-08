"""Small, deterministic demonstration of all three ordered-set interfaces."""

from structures import TREE_TYPES, make_tree


def main():
    """Input: none. Output: validated insert/search/delete demonstrations."""
    for name in TREE_TYPES:
        tree = make_tree(name)
        print(f"\n{name.upper()}")
        for key in (30, 10, 20, 50, 40):
            print(f"  insert({key}) -> {tree.insert(key)}")
        print(f"  insert(20) again -> {tree.insert(20)}")
        print(f"  contains(40) -> {tree.contains(40)}")
        print(f"  contains(99) -> {tree.contains(99)}")
        print(f"  delete(30) -> {tree.delete(30)}")
        print(f"  delete(99) -> {tree.delete(99)}")
        tree.validate()
        print(f"  sorted keys -> {list(tree.inorder())}")
        print(f"  live keys -> {len(tree)}; array storage -> {tree.storage_bytes()} bytes")


if __name__ == "__main__":
    main()
