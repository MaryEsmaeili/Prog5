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