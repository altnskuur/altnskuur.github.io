# std::vector

`std::pmr::vector` comes with C++20. `std::vector` and `std::pmr::vector` are not same.

```c++
template<
    class T,
    class Allocator = std::allocator<T>
> class vector;
```

```c++
namespace pmr {
    template< class T >
    using vector = std::vector<T, std::pmr::polymorphic_allocator<T>>;
}
```

Default to `std::vector`. It's the right choice for almost all code: it's simple, every library and API expects it, and the heap is fast enough for most programs. If you're not sure, use `std::vector`.

Use `std::pmr::vector` when memory allocation itself becomes a problem you need to control. Typical situations:

- Many short-lived allocations in a hot loop.
```c++
void handleRequest(const Request& req) {
    std::array<std::byte, 64 * 1024> scratch;   // 64 KB on the stack
    std::pmr::monotonic_buffer_resource arena(scratch.data(), scratch.size());

    std::pmr::vector<Token> tokens(&arena);     // all temporary data uses the arena
    std::pmr::vector<Node> nodes(&arena);
    ...
}   // arena is destroyed here: everything freed at once, no per-element deletes
```

- Where heap allocation is not allowed.
- Nested containers sharing one resource
- Tracking or limiting memory

|  | `std::array<T, N>` | `std::vector<T>` |
|---|---|---|
| Size | Fixed at compile time; part of the type | Decided at runtime; can change |
| Memory | Inside the object itself (stack, or inside the containing object) | Heap |
| Allocation cost | None | Allocates when created/grows |
| Grow/shrink | Not possible | `push_back`, `resize`, `erase`... |
| Object size | Exactly `N * sizeof(T)` | ~24 bytes (3 pointers) + heap block |
| Copy | Copies all `N` elements | Copies all elements (heap allocation too) |
| Move | Still copies element by element | Cheap: steals the heap pointer |
| Pointers into it | Stay valid as long as the array lives | Invalidated when it reallocates |
| Contiguous, has `data()`, works with `std::span` | Yes | Yes |

### Member Functions

|  |  |
|---|---|
| (constructor) | constructs a `vector` |
| `operator=`   | assigns a `vector`   |
| `assign` | assigns values to the container |
| `assign_range` [C++23] | assigns a range of values to the container |
| `get_allocator` | returns the associated allocator |
| (destructor) | destructs a `vector`   |

**[C++23] Note:** It's newer than the others, so it needs both C++23 mode and a recent standard library (for example GCC 15 or a recent Visual Studio). If your compiler says `assign_range` doesn't exist, use `v.assign(r.begin(), r.end())` instead; the result is the same.

Element Access

|  |  |
|---|---|
| `at` | returns the element at an index, with **bounds checking** |
| `operator[]` | returns the element at an index, with **no-bounds checking** |
| `front` | returns the first element, the same as `v[0]`. |
| `back` | returns the last element, the same as `v[v.size() - 1]` |
| `data`   | returns a raw pointer to the first element. Used to pass vector contents to functions that take a pointer, like C APIs, `std::memcpy`, or file writes. |

**Warning:** the pointer from `data()` (like any pointer, reference, or iterator into the vector) becomes invalid when the vector reallocates:

```c++
int* p = v.data();
v.push_back(60);         // may reallocate and move all elements
*p;                      // dangerous: p might point to freed memory
```

Get a fresh pointer with `data()` after anything that can grow the vector.

Iterators

|  |  |
|---|---|
| `begin`    `cbegin`  [C++11] | returns an iterator to the beginning |
| `end`    `cend`  [C++11] | returns an iterator to the end |
| `rbegin`  `crbegin` [C++11] | returns a reverse iterator to the beginning |
| `rend`  `crend` [C++11] | returns a reverse iterator to the end |

**[C++23] Note:** The iterators that came with C++23, are for `const`. These iterators is just read-only.

**Example** for span of `‘a’, ’b’, ’c’`:

```
index:     -1     0     1     2     3   
					rend   'a'   'b'   'c'   end
								begin       rbegin
```

**Capacity**

|  |  |
|---|---|
| `empty` | returns `true` if the vector has no elements |
| `size` | how many elements are in the vector right now |
| `max_size` | the theoretical maximum number of elements the vector could ever hold on this system. It's a huge number, limited by the address space, not by your actual RAM |
| `reserve` | makes sure the capacity is at least `n`, allocating once up front. |
| `capacity` | how many elements fit in the currently allocated memory before the vector has to reallocate |
| `shrink_to_fit` [DR*] | asks the vector to free unused capacity, so that capacity matches size |

**Note about** `capacity`**:** With GCC, you'd typically see capacity jump 1, 2, 4, 8, 16 (doubling). With Visual Studio, it grows by about 1.5×. Each jump is a reallocation: new memory, all elements moved, old memory freed, and every old pointer and iterator invalidated.

**Note about** `shrink_to_fit`**:**  

```c++
std::vector<int> v(1000);   // 1000 elements
v.resize(10);               // size 10, but capacity is still 1000
v.capacity();               // 1000: memory not returned

v.shrink_to_fit();
v.capacity();               // usually 10 now
```

**About** `[DR*]`**:** on cppreference, "DR" means **defect report**, a correction to the C++ standard that's applied retroactively to older versions as well. It's a note about the official wording having been fixed, not a feature you need to enable. You can use `shrink_to_fit` normally in C++11 and later.

**Modifiers**

|  |  |
|---|---|
| `clear`   | removes all elements. size becomes 0, but the **capacity stays** (the memory is kept for reuse) |
| `insert` | inserts at any position, given as an **iterator. elements after that position shift right, so inserting in the middle is slow (O(n)).** |
| `insert_range` [C++23] | like `insert` with an iterator range, but takes the whole range directly: |
| `emplace` [C++11] | like `insert`, but builds the element in place from constructor arguments, as `emplace_back` does, at any position. |
| `erase` | removes one element or a range, given by iterators. Later elements shift left. It returns an iterator to the element after the removed ones. |
| `push_back` | adds an element at the end. Fast (amortized O(1)). |
| `emplace_back` [C++11] | adds at the end, but **builds the element directly inside the vector** from the arguments you give, instead of creating it first and then copying or moving it in |
| `append_range` [C++23] | adds a whole range at the end. It's the same as `insert_range(v.end(), r)`, but shorter. |
| `pop_back` | removes the last element |
| `resize` | changes the **size** |
| `swap` | exchanges the full contents of two vectors. it's very fast, because only the internal pointers are swapped; no elements are copied. |

**Difference between** `push_back` **and** `emplace_back`  

```c++
std::vector<Point> pts;
pts.push_back(Point(1, 2));   // creates a temporary Point, then moves it in
pts.emplace_back(3, 4);       // constructs Point(3, 4) directly in place
```

Since C++17, it also returns a reference to the new element: `auto& p = pts.emplace_back(5, 6);`. For simple types like `int`, there's no practical difference from `push_back`.

**Example** for `insert_range`:

```c++
std::vector<int> v{1, 5};
std::array<int, 3> mid{2, 3, 4};
v.insert_range(v.begin() + 1, mid);   // {1, 2, 3, 4, 5}
```

**Example** for `erase`:

```c++
std::vector<int> v{1, 2, 3, 4, 5};
v.erase(v.begin() + 1);               // remove index 1: {1, 3, 4, 5}
v.erase(v.begin(), v.begin() + 2);    // remove the first two: {4, 5}
```

Non-Member Functions

|  |  |
|---|---|
| operator== |  |
| operator!= | removed in C++20 |
| operator< | removed in C++20 |
| operator<= | removed in C++20 |
| operator> | removed in C++20 |
| operator>= | removed in C++20 |
| operator<=> | C++20 |

### What changed in C++20

In C++20, `std::vector` only defines two of these: `operator==` and `operator<=>` (the "three-way comparison," also called the spaceship operator). The others (`!=`, `<`, `<=`, `>`, `>=`) were removed from the library, which is why cppreference marks them "(removed in C++20)." Your code doesn't change, though: the compiler now rewrites them automatically. `a != b` becomes `!(a == b)`, and `a < b` becomes `(a <=> b) < 0`.

`<=>` returns a single result saying whether the left side is less, equal, or greater:

```c++
auto r = a <=> c;
if (r < 0)  std::cout << "a is smaller";
if (r == 0) std::cout << "equal";
if (r > 0)  std::cout << "a is bigger";
```

So instead of writing six operators, a type writes two and gets all six. That's a nice trick for your own classes too.

# References

[1] [https://en.cppreference.com/cpp/container/vector](https://en.cppreference.com/cpp/container/vector)

[2] [https://www.geeksforgeeks.org/cpp/vector-in-cpp-stl/](https://www.geeksforgeeks.org/cpp/vector-in-cpp-stl/)
