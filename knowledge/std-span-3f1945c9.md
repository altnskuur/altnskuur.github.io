# std::span

std::span comes with C++20.

```c++
template<class T, std::size_t Extent = std::dynamic_extent>
class span;
```

The class template `span` describes an object that can refer to a contiguous sequence of objects with the first element of the sequence at position zero. A `span` can either have a *static* extent, in which case the number of elements in the sequence is known at compile-time and encoded in the type, or a *dynamic* extent. [1]

### Quick Notes

> 💡
> - Non-ownership/No Memory Allocation. Cost is only a pointer and a length variable. 
> - Recognizing just sequential datas in memory
> - If length can be calculated in compile time, give the second parameter like `std::span<std::uint8_t, dataLength>`. If it cannot, leave there empthy for default parameter `std::dynamic_extent`.

### Data Members

| Member | Description |
|---|---|
| **extent** [static] | Extent - public static member constant. |
| `pointer` data_ | a pointer to the underlying sequence |
| `size_type` size_ | the number of elements |

### Member Functions

|  |  |
|---|---|
| (constructor) | constructs a span  |
| `operator=`   | assigns a `span`   |
| (destructor) | destructs a `span`     |

Iterators

|  |  |
|---|---|
| `begin`  `cbegin` [C++23] | returns an iterator to the beginning  |
| `end`    `cend` [C++23] | returns an iterator to the end  |
| `rbegin`    `crbegin` [C++23] | returns a reverse iterator to the beginning  |
| `rend`    `crend` [C++23] | returns a reverse iterator to the end  |

**[C++23] Note:** The iterators that came with C++23, are for `const`. These iterators is just read-only.

**Example** for span of `‘a’, ’b’, ’c’`:

```
index:     -1     0     1     2     3   
					rend   'a'   'b'   'c'   end
								begin       rbegin
```

Element Access

|  |  |
|---|---|
| `front`   | access the first element (same as s[0])  |
| `back` | access the last element (same as s[s.size() -1])  |
| `at` [C++26] | access specified element with bounds checking  |
| `opertator[]`   | access specified element (same as s[i] operator)  |
| `data`   | direct access to the underlying contiguous storage (returns raw pointer)  |

**[C++26] Note:**  `at(i)` element access function same as `s[i]`. But difference is that `at` checks the index first. `operator[]` does **no bounds checking**. `at` function is checks bounds. If `i >= size()`, it throws `std::out_of_range`.

Observers

|  |  |
|---|---|
| `size` | returns the number of **elements** |
| `size_bytes` | returns the size of the sequence in **bytes** |
| `empty`   | checks if the sequence is empty  |

Subviews

|  |  |
|---|---|
| `first` | obtains a subspan consisting of the first `N` elements of the sequence |
| `last` | obtains a subspan consisting of the last `N` elements of the sequence |
| `subspan` | obtains a subspan |

**Example** for subviews:

```
index:     0     1     2 ... n ... (k-m) ... (k-1)     k
          |-------------------|   |---------------------|
               s.first(n)                s.last(m)
                      |---------------------------------|
                                s.subspan(2)
                            |---------------------|
                             s.subspan(n, (k-1)-n)
```

Non-Member Functions

|  |  |
|---|---|
| `as_bytes` [C++20] | converts a `span` into a view of its underlying bytes |
| `as_writable_bytes` [C++20] |  |

The only difference between `as_bytes` and `as_writable_bytes` is permission:

- `std::as_bytes` returns `std::span<const std::byte>`. You can read the bytes, but the compiler won't let you change them.
- `std::as_writable_bytes` returns `std::span<std::byte>`. You can read the bytes and change them. And yes, since it points to the same address, changing a byte changes the original data directly.

**Example** for `as_bytes`:

```c++
std::uint32_t x = 0x11223344;
std::span<std::uint32_t> numbers(&x, 1);   // a view of 1 number

auto bytes = std::as_bytes(numbers);        // a view of its 4 bytes

for (std::byte b : bytes)
    std::printf("%02x ", std::to_integer<int>(b));
// prints: 44 33 22 11
```

**Example** for `as_writable_bytes`:

```c++
std::uint32_t x = 0x11223344;
std::span<std::uint32_t> numbers(&x, 1);

auto r = std::as_bytes(numbers);
r[0] = std::byte{0xFF};      // compile error: read-only

auto w = std::as_writable_bytes(numbers);
w[0] = std::byte{0xFF};      // OK, and now x itself is 0x112233FF
```

# References

[1] [https://en.cppreference.com/cpp/container/span](https://en.cppreference.com/cpp/container/span)
