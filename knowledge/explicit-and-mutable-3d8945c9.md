---

# `explicit` Keyword

## Constructors Is Defined With Single Parameters

```c++
class Distance {
	
	private:
		const float MTF;
		int feet;
		float inches;
		
	public:
		Distance() : feet(0), inches(0.0), MTF(3.280833F) { } 
		explicit Distance(float meters) : MTF(3.280833F) {
		
		float fltfeet = MTF * meters;
		feet = int(fltfeet - feet);
		inches = 12*(fltfeet - feet);
		}
};
```

When we instantiate an object in the main function like `Distance d1(20);`, if the constructor is marked as explicit, the compiler will not allow this implicit type conversion. Without the explicit keyword, the compiler would implicitly convert the integer 20 to a float (or match the constructor).

## Conversion Operators

### What is a Conversion Operator and How is it Defined

```c++
class Distance {
    float meters;
public:
    // Sınıfı float'a dönüştüren operatör
    operator float() const {
        return meters; 
    }
};
```

```c++
Distance dist(5.5F);
float m = dist; // Distance object convert float automatically.
```

**What is the problematic point?** Similar to single-parameter constructors, C++ tends to be overly "helpful" in this context. Omitting safeguards on a conversion operator allows the compiler to perform hidden conversions in hazardous situations, such as:

- Passing a `Distance` object to a function that expects a `float` by mistake.
- Performing arithmetic operations (e.g., `Distance dist; float result = dist + 3.2f;`), where the compiler silently converts the object into a `float` and proceeds arbitrarily.

This can occasionally lead to subtle and illogical bugs. Since the compiler automatically handles the conversion when the object shouldn't logically participate in a numerical addition, the underlying error remains undetected.

Right at this point, Modern C++ (C++11 and later) gives us the ability to put the `explicit` keyword in front of conversion operators as well.

```c++
class Distance {
    float meters;
public:
    // Now explicit!
    explicit operator float() const {
        return meters; 
    }
};
```

```c++
Distance dist(5.5F);

float m = dist;          // Compile Error
printFloat(dist);        // Compile Error
```

Here is the core of the matter:

- Yes, the function exists: Since `operator float()` is defined, C++ knows very well how to perform that conversion.
- But `explicit` forbids it: The sole purpose of the `explicit` keyword is to prevent implicit conversions.

# `mutable` Keyword

## `mutable` Data Members

- **Where it is used:** At the beginning of a regular member variable inside a class.
- **What it does:** Allows that specific variable's value to be modified even if the object itself is `const` (e.g., `mutable string owner;` or `mutable int cacheValue;`).
- **Scope/Purpose:** Used to preserve **logical constness**, implement caching mechanisms, or hold a thread-safe `mutex` inside a read-only object.

```c++
class scrollbar {
    int size;
    mutable string owner;   // Ownership: mutable! even in const object, it can be changed
public:
    void setOwner(string own) const {  // const function! Normally data cannot change by this way
        owner = own; // but owner variable is "mutable"!
    }
};
```

```c++
const scrollbar sbar(60, "Window1"); // object totally const!

// sbar.setSize(100); // ERROR! size is not mutable, it doesn't be change in a const object.
sbar.setOwner("Window2"); // IT WORKS! Bcs owner is marked as mutable
```

## Lambda Expressions

- **Where it is used:** In the signature of a lambda function, right after the parameter parentheses (`(...) mutable { ... }`).
- **What it does:** Allows variables captured "by value" (via copy) from the outer scope to be modified inside the lambda body.

```c++
int counter = 0;
auto increment = [counter]() mutable {
    counter++; // Normally, the copied 'counter' is const and cannot be modified.
               // But with 'mutable', you can modify the internal copy!
};
```

---

## What is its Real Purpose in Software Development? (Logical Constness)

Behind this concept in C++, there are two types of "constness" definitions:

1. **Bitwise Constness (Physical Constness):** This is the perspective of the C++ compiler. The compiler states: *"If an object is* `const`*, no bits (no member variables) in memory can be modified."*
2. **Logical Constness:** This is the programmer's perspective. It implies: *"From an outside observer's point of view, this object remains logically unchanged (e.g., a window's size or position stays the same), but some internal auxiliary data like performance enhancements, caching, or ownership can be updated."*

The `mutable` keyword exists precisely to implement **Logical Constness**.

**Real-World Software Scenarios (Where is it used?):**

- **Caching and "Lazy Evaluation":** You might have a `const` object perform a heavy mathematical calculation inside a `const` function. To avoid recomputing the result every time, you store it in a `mutable int cachedResult;`. Even though the object is `const`, the function can write the computed result into that `mutable` cache variable. To an outside observer, the object has not changed (it is logically constant), but an internal performance optimization has been achieved.
- **Thread Safety and Mutexes:** When writing multithreaded code, you may want to ensure safe reading of data from a `const` object. To lock the object while reading it without altering its logical data, you use a `mutable std::mutex`. Because the mutex does not change the object's logical state, it is declared `mutable`, allowing `lock()` and `unlock()` operations to be called even on a `const` object.
- **Counters (Logging / Statistics):** To track how many times a particular function of an object has been accessed, you can include a `mutable int accessCount;` inside it, incrementing it every time a `const` function is called.
