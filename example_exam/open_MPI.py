from mpi4py import MPI
import math
import argparse

def trapezoid_method(func, l_bound, u_bound, n_steps):
    """
    Approximate the integral using the trapezoidal rule.

    Parameters:
    func (function): The function to integrate.
    l_bound (float): The lower bound of the integral.
    u_bound (float): The upper bound of the integral.
    n_steps (int): The number of trapezoids used in the approximation.

    Returns:
    float: The approximate value of the integral.
    """
    step_size = (u_bound - l_bound) / n_steps
    total = 0.5 * (func(l_bound) + func(u_bound))
    for i in range(1, n_steps):
        total += func(l_bound + i * step_size)
    return total * step_size

def parallel_trapezoid(func, a, b, n):
    """
    Perform parallelized trapezoidal integration using MPI Reduce.

    Parameters:
    func (function): The function to integrate.
    a (float): Lower bound of the integration interval.
    b (float): Upper bound of the integration interval.
    n (int): Total number of steps for integration.

    Returns:
    float: The integral result calculated by the root process.
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Each process works on its subinterval
    step_size = (b - a) / n
    local_n = n // size
    local_a = a + rank * local_n * step_size
    local_b = local_a + local_n * step_size
    local_integral = trapezoid_method(func, local_a, local_b, local_n)

    # Reduce all local_integral values to get the total integral
    total_integral = comm.reduce(local_integral, op=MPI.SUM, root=0)

    if rank == 0:
        return total_integral
    return None

def parse_arguments():
    """
    Parse command-line arguments for numerical integration.
    """
    parser = argparse.ArgumentParser(description="Parallel trapezoidal integration using MPI Reduce")
    parser.add_argument('-a', type=float, required=True, help='Lower bound of integration')
    parser.add_argument('-b', type=float, required=True, help='Upper bound of integration')
    parser.add_argument('-n', type=int, required=True, help='Number of steps for the trapezoid method')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    result = parallel_trapezoid(math.cos, args.a, args.b, args.n)
    if MPI.COMM_WORLD.Get_rank() == 0:
        exact_result = math.sin(args.b) - math.sin(args.a)
        error = abs(exact_result - result)
        print(f"n={args.n}, Integral Result={result}, Error={error}")
