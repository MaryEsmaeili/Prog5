from mpi4py import MPI
import math
import argparse

def exact_integral(low_b, up_b):
    """Calculate the exact value of the integral of cos(x) over the interval."""
    return math.sin(up_b) - math.sin(low_b)

def trapezoid_method(func, l_bound, u_bound, n_steps):
    """Apply the trapezoid method to approximate the integral."""
    step_size = (u_bound - l_bound) / n_steps
    total = 0.5 * (func(l_bound) + func(u_bound))
    for i in range(1, n_steps):
        total += func(l_bound + i * step_size)
    return total * step_size

def parallel_trapezoid(min_bound, max_bound, num_steps):
    """Perform parallelized trapezoidal integration using MPI."""
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    step_size = (max_bound - min_bound) / num_steps
    local_steps = num_steps // size
    local_a = min_bound + rank * local_steps * step_size
    local_b = local_a + local_steps * step_size
    local_result = trapezoid_method(math.cos, local_a, local_b, local_steps)

    total_result = comm.reduce(local_result, op=MPI.SUM, root=0)

    if rank == 0:
        return total_result
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parallel trapezoidal integration using MPI")
    parser.add_argument('-a', type=float, required=True, help='Lower bound of integration')
    parser.add_argument('-b', type=float, required=True, help='Upper bound of integration')
    parser.add_argument('-n', type=int, required=True, help='Number of steps for the trapezoid method')

    args = parser.parse_args()

    result = parallel_trapezoid(args.a, args.b, args.n)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        exact_result = exact_integral(args.a, args.b)
        error = abs(exact_result - result)
        print(f"n={args.n}, error={error}")
