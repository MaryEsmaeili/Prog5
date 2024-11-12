import matplotlib.pyplot as plt

# Load timing data
async_times = []
original_times = []
worker_counts = []

# Read asynchronous version times
with open("async_times.txt") as f:
    for line in f:
        count, time = line.split()
        worker_counts.append(int(count))
        async_times.append(float(time))

# Read original version times
with open("original_times.txt") as f:
    for line in f:
        _, time = line.split()
        original_times.append(float(time))

# Plotting
plt.plot(worker_counts, async_times, label='Asynchronous Version', marker='o')
plt.plot(worker_counts, original_times, label='Original Version (assignment2.py)', marker='s')
plt.xlabel("Number of Workers")
plt.ylabel("Execution Time (seconds)")
plt.title("Execution Time Comparison")
plt.legend()
plt.grid(True)

plt.savefig("gather_vs_irecv.png", format="png")

print("Plot saved as gather_vs_irecv.png")

