# The Wrong Scenario: What If Parameters Were Passed By-Value?

Suppose C++ rules allowed it, and you wrote your copy constructor like this:

```c++
class Test {
public:
    // WRONG (Simulation): Parameter is passed by-value
    Test(Test other) { 
        // copying logic...
    }
};

int main() {
    Test t1;
    Test t2 = t1; // We want to create t2 using t1
}
```

**The Disaster Behind the Scenes (Infinite Recursion):**

1. When you write `Test t2 = t1;`, the compiler wants to invoke that copy constructor taking `t1` as a parameter: `Test(Test other)`.
2. The fundamental rule of C++ function calls is: If a parameter is passed **by-value**, a temporary **clone (copy)** of that parameter must be created *before* entering the function body.
3. To create a copy of `t1`, you need to instantiate a brand-new object in memory. And what function gets called to instantiate a new object through copying? Why, the **Copy Constructor (**`Test(Test other)`**)** itself!
4. That newly invoked copy constructor also tries to take its parameter by-value, which *again* forces a copy to be made → **Steps 3 and 4 repeat infinitely (Infinite Recursion).**

The program crashes before the function can even execute, trapped inside an endless loop just trying to pass the parameter.

# The Correct Scenario: How Reference (`&`) Breaks the Loop

To prevent this catastrophe, C++ forces the copy constructor's parameter to be **a reference (**`&`**)**:

```c++
class Test {
public:
    // CORRECT: Using a reference (&)
    Test(const Test& other) { 
        // t1's data is copied into t2
    }
};
```

**Why does this work?**

- The moment you add the `&` **(reference)**, the compiler does **not** create a new copy when passing the argument into the function.
- Instead, it simply binds the existing object's (`t1`'s) memory address (an alias) directly into the function scope.
- Since there is no attempt to "create a new copy" just to pass the argument, no secondary constructor is triggered. The infinite loop is successfully averted!
- The preceding `const` ensures that your code inside the constructor cannot accidentally corrupt or mutate the original object's (`t1`'s) data.

> **Summary:** A function tasked with creating copies cannot rely on *making a copy of itself* just to be called. Therefore, the object must be passed into the constructor via its **address (reference)** instead of by value.
