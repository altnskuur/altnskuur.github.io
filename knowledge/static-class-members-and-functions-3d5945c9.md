```c++
class CountClassNumber {

	private: 
		static int totalCount;
		int id;
	
	public:
		CountClassNumber() {
		
			totalCount++;
			id = totalCount;
		}
		
		~CountClassNumber() {
		
			totalCount--;
			std::cout << "Destroying ID Number " << id << std::endl;
		}
		
		static void showTotal() {
		
			std::cout << "Total Count is " << totalCount << std::endl;
		}
		
		void showID() {
			
			std::cout << "ID is " << id << std::endl;
		}
};

int CountClassNumber::totalCount = 0;

int main() {
	
	CountClassNumber cl1;
	CountClassNumber::showTotal();
	
	CountClassNumber cl2, cl3;
	CountClassNumber::showTotal();
	
	cl1.showID();
	cl2.showID();
	cl3.showID();
	
	std::cout << "-----end of program-----" << std::endl;
	
	return 0;
}
```

**Output:**

```
Total Count is 1
Total Count is 3
ID is 1
ID is 2
ID is 3
-----end of program-----
Destroying ID Number 3
Destroying ID Number 2
Destroying ID Number 1
```

### Why did we define `totalCount` with `static` specifier?

In this code, we want to count total class number. If we define without `static` specifier, we cannot use variable that is same for all classes. When we add static keyword, we earn these:

- Variable created when program starts, and live till program ends.
- All of classes that is type of `CountClassNumber` uses same and just one variable
- Static variables in the class is not connected with objects, it just belongs to this class.

### Why did we initialize `totalCount` explicitly like `int CountClassNumber::totalCount = 0` ?

Class definition is just a template. If we have a static member in the class, we must initialize this member outside of the class. At this point we have 2 option:

1. Initialize variable to out of the class like `int CountClassNumber::totalCount = 0`  
2. Initialize inside of the class with `inline`  specifier like `inline static int totalCount = 0;`. 
  If we define like just `static int totalCount = 0;`, we can take “Multiple Definitions” error because of multiple inluding of that class. So we connect all of the `static int totalCount` variables with inline keyword.

### How did we check `totalCount` number with `CountClassNumber::showTotal()`  

We define our function `showTotal()` with `static` specifier. This specifier brings our functions calling like `CountClassNumber::showTotal()`.

How does it useful for us?

When you open the project and write some codes on your page, how can you know how many classes created? You must define a variable for learning class count. But maybe you want to see number of class without creating any class. This `static` function keyword gives a change to us that calling function without any connection of object.
