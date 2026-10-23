# this is a small demonstration of the three ordered-set implementations.
from structures import TREE_TYPES, make_tree

def main():
    # Input: none
    # Output: example results for insert, search and delete
    for name in TREE_TYPES:
        tree = make_tree(name)
        for key in (40, 20, 60, 10, 30, 50, 70):
            tree.insert(key)

        print(f"\n{name.upper()}")
        print("After insert:", list(tree.inorder()))
        print("Search 30:", tree.search(30))
        print("Search 99:", tree.search(99))
        print("Duplicate 30:", tree.insert(30))
        print("Delete 40:", tree.delete(40))
        print("After delete:", list(tree.inorder()))
        print("Height:", tree.height())
        print("Array storage (bytes):", tree.storage_bytes())

if __name__ == "__main__":
    main()
