from mpi4py import MPI
import argparse
import numpy as np
import math

# Function for exact integral
def exact_integral(lower_bound, upper_bound):
    return math.sin(upper_bound) - math.sin(lower_bound)

# Trapezoid rule implementation
def trapezoid_method(func, lower_bound, upper_bound, n):
    h = (upper_bound - lower_bound) / n
    total = 0.5 * (func(lower_bound) + func(upper_bound))
    for i in range(1, n):
        total += func(lower_bound + i * h)
    return total * h

# Main MPI parallelized function
def parallel_trapezoid(lower_bound, upper_bound, n):
    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()  # Process rank
    size = comm.Get_size()  # Total number of processes

    # Divide the interval among workers
    h = (upper_bound - lower_bound) / n
    local_n = n // size  # Divide steps equally among ranks
    local_a = lower_bound + rank * local_n * h
    local_b = local_a + local_n * h

    # Each process computes the trapezoidal approximation on its subinterval
    local_result = trapezoid_method(math.cos, local_a, local_b, local_n)

    # Master process gathers all results
    if rank == 0:
        total_result = local_result
        for i in range(1, size):
            local_result = comm.recv(source=i)
            total_result += local_result
        return total_result
    else:
        # Send results back to the master process
        comm.send(local_result, dest=0)

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Parallel trapezoidal integration using MPI')
    parser.add_argument('-a', type=float, required=True, help='Lower bound of integration')
    parser.add_argument('-b', type=float, required=True, help='Upper bound of integration')
    parser.add_argument('-n', type=int, required=True, help='Number of steps for the trapezoid method')
    return parser.parse_args()

# Main function
if __name__ == "__main__":
    args = parse_arguments()
    lower_bound = args.a
    upper_bound = args.b
    n = args.n

    # MPI parallelized trapezoidal integration
    result = parallel_trapezoid(lower_bound, upper_bound, n)

    # Rank 0 will handle output
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        exact_result = exact_integral(lower_bound, upper_bound)
        error = abs(exact_result - result)
        print(f"n={n}, error={error}")
