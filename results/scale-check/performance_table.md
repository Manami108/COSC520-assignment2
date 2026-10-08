# Measured performance

Generated from raw.csv; time is batch median.

| Order | Workload | n | Structure | Operation | Median seconds | Median us/op | Min-max us/op | Repeats |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| random | uniform | 100,000 | avl | build | 1.419932 | 14.1993 | 14.1993-14.1993 | 1 |
| random | uniform | 100,000 | splay | build | 1.510561 | 15.1056 | 15.1056-15.1056 | 1 |
| random | uniform | 100,000 | treap | build | 0.589586 | 5.8959 | 5.8959-5.8959 | 1 |
| random | uniform | 1,000,000 | avl | build | 20.977428 | 20.9774 | 20.9774-20.9774 | 1 |
| random | uniform | 1,000,000 | splay | build | 19.841870 | 19.8419 | 19.8419-19.8419 | 1 |
| random | uniform | 1,000,000 | treap | build | 7.608911 | 7.6089 | 7.6089-7.6089 | 1 |
| random | uniform | 100,000 | avl | delete | 0.016269 | 16.2687 | 16.2687-16.2687 | 1 |
| random | uniform | 100,000 | splay | delete | 0.020775 | 20.7751 | 20.7751-20.7751 | 1 |
| random | uniform | 100,000 | treap | delete | 0.006689 | 6.6893 | 6.6893-6.6893 | 1 |
| random | uniform | 1,000,000 | avl | delete | 0.030645 | 30.6448 | 30.6448-30.6448 | 1 |
| random | uniform | 1,000,000 | splay | delete | 0.025246 | 25.2464 | 25.2464-25.2464 | 1 |
| random | uniform | 1,000,000 | treap | delete | 0.007689 | 7.6886 | 7.6886-7.6886 | 1 |
| random | uniform | 100,000 | avl | insert | 0.012777 | 12.7766 | 12.7766-12.7766 | 1 |
| random | uniform | 100,000 | splay | insert | 0.007257 | 7.2575 | 7.2575-7.2575 | 1 |
| random | uniform | 100,000 | treap | insert | 0.004316 | 4.3157 | 4.3157-4.3157 | 1 |
| random | uniform | 1,000,000 | avl | insert | 0.021395 | 21.3955 | 21.3955-21.3955 | 1 |
| random | uniform | 1,000,000 | splay | insert | 0.007101 | 7.1009 | 7.1009-7.1009 | 1 |
| random | uniform | 1,000,000 | treap | insert | 0.005016 | 5.0164 | 5.0164-5.0164 | 1 |
| random | uniform | 100,000 | avl | search | 0.003757 | 1.8784 | 1.8784-1.8784 | 1 |
| random | uniform | 100,000 | splay | search | 0.010491 | 5.2455 | 5.2455-5.2455 | 1 |
| random | uniform | 100,000 | treap | search | 0.004183 | 2.0914 | 2.0914-2.0914 | 1 |
| random | uniform | 1,000,000 | avl | search | 0.005165 | 2.5823 | 2.5823-2.5823 | 1 |
| random | uniform | 1,000,000 | splay | search | 0.009569 | 4.7843 | 4.7843-4.7843 | 1 |
| random | uniform | 1,000,000 | treap | search | 0.005669 | 2.8344 | 2.8344-2.8344 | 1 |
