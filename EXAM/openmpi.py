from mpi4py import MPI
import numpy as np

# Define the integration bounds and step size
lower_bound = 0.0
upper_bound = 1.0
num_steps = 1000000
step_size = (upper_bound - lower_bound) / num_steps

# Define the function to integrate (example: f(x) = x^2)
def function_to_integrate(x):
    return x**2

# Compute the local integral for each process
def compute_local_integral(start, end, step_size):
    integral = 0.0
    x = start
    while x < end:
        integral += function_to_integrate(x) * step_size
        x += step_size
    return integral

# MPI setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Define the bounds each rank should handle
work_per_rank = (upper_bound - lower_bound) / (size - 1)  # Exclude rank 0

# Broadcast step size to all processes
step_size = comm.bcast(step_size, root=0)

# Asynchronous gathering of results at rank 0
if rank == 0:
    # Rank 0 initializes asynchronous receiving
    requests = []
    results = np.zeros(size - 1)
    for i in range(1, size):
        req = comm.irecv(source=i, tag=10)
        requests.append(req)
    
    # Wait for each result and sum up
    for i in range(size - 1):
        results[i] = requests[i].wait()  # Wait for each irecv request to complete
    
    # Calculate the final integral result
    final_result = np.sum(results)
    print(final_result)

else:
    # Calculate the start and end points for this rank's work
    start_point = lower_bound + (rank - 1) * work_per_rank
    end_point = start_point + work_per_rank
    
    # Compute the local integral on this rank's portion
    local_integral = compute_local_integral(start_point, end_point, step_size)
    
    # Send the result back to rank 0
    comm.send(local_integral, dest=0, tag=10)
