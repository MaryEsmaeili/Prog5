### Analysis of Results:
## Part 1
1. **When does adding more cores no longer improve performance?**
   - Performance improvements stop after 4 cores. The best time (0.71 seconds) is achieved at 4 cores. Beyond that, adding more cores results in **diminishing returns**, and after 8 cores, the time actually increases.

2. **Why does this happen?**
   - The main reason for this behavior is the **overhead** associated with managing parallel tasks:
     - **Increased communication cost**: As the number of cores increases, the system needs to coordinate and manage more communication between the cores, which leads to overhead that slows down the program.
     - **I/O and memory bottlenecks**: If the problem is not large enough, memory bandwidth or I/O can become a bottleneck, limiting the benefits of parallelism.
     - **Workload imbalance**: If the tasks are not perfectly balanced across cores, some cores may finish earlier and stay idle while others are still processing, leading to inefficiencies.

In onclusion while increasing the number of cores improves performance initially (from 2 to 4), further increases in core count lead to diminishing returns due to communication overhead and other system limitations. The sweet spot for this problem seems to be **4 cores**, as that yields the best time with the least overhead.

## Part 2
### 1. **Where is the most calculation time spent?**
   - The function that takes up the **most calculation time** is the `trapezoid_method` function, which is responsible for performing the trapezoidal integration. This function accounts for **2.538 seconds** out of the total 4.996 seconds of execution time.
   - The second highest contributor to execution time is the **math.cos** function, which is called **1,000,001 times** and takes **2.433 seconds**.

### 2. **Which line number/function is it?**
   - The **trapezoid_method** function, located at line 23 in `assignment1.py`, is responsible for most of the computation time.
   - The **math.cos** function, which is used in the trapezoidal approximation, is the next major contributor to the execution time.

### 3. **What is the distribution of execution times?**
   - The **distribution of execution times** follows a **power distribution**, where a small number of functions (like `trapezoid_method` and `math.cos`) take up the vast majority of the execution time. 
   - Other functions (such as imports, argument parsing, or smaller helper functions) contribute negligibly to the total execution time. This is characteristic of a **power distribution**, where most of the execution time is concentrated in a few “heavy” functions, while many other functions take little or no time.

### Summary for `assignment5.md`:
- The profiling shows that the `trapezoid_method` function (line 23) is the most time-consuming part of the code, taking approximately 2.538 seconds.
- The `math.cos` function is called frequently (1,000,001 times) and takes 2.433 seconds.
- The execution time is not uniform; rather, it follows a power distribution, where the bulk of the time is spent in a small number of functions (`trapezoid_method` and `math.cos`), with the rest of the functions contributing only marginally.
