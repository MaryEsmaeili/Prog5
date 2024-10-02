"""
This module implements parallelized numerical integration using the trapezoid rule 
with OpenMPI.
"""

import argparse
import math
from mpi4py import MPI

def exact_integral(low_b, up_b):
    """
    Calculate the exact value of the integral of cos(x) over the interval.

    Parameters:
    low_b (float): Lower bound of the integration interval.
    up_b (float): Upper bound of the integration interval.

    Returns:
    float: Exact value of the integral.
    """
    return math.sin(up_b) - math.sin(low_b)

def trapezoid_method(func, l_bound, u_bound, n_steps):
    """
    Apply the trapezoid method to approximate the integral of a function.

    Parameters:
    func (function): The function to integrate.
    l_bound (float): Lower bound of the integration interval.
    u_bound (float): Upper bound of the integration interval.
    n_steps (int): Number of steps in the approximation.

    Returns:
    float: The approximated value of the integral.
    """
    step_size = (u_bound - l_bound) / n_steps
    total = 0.5 * (func(l_bound) + func(u_bound))
    for i in range(1, n_steps):
        total += func(l_bound + i * step_size)
    return total * step_size

def parallel_trapezoid(min_bound, max_bound, num_steps):
    """
    Perform parallelized trapezoidal integration using MPI.

    Parameters:
    l_bound (float): Lower bound of the integration interval.
    u_bound (float): Upper bound of the integration interval.
    n_steps (int): Number of steps in the approximation.
    
    Returns:
    float: The parallelized approximation of the integral, or None for worker ranks.
    """
    api_comm = MPI.COMM_WORLD
    my_rank = api_comm.Get_rank()
    size = api_comm.Get_size()
    step_size = (max_bound - min_bound) / num_steps
    local_steps = num_steps // size
    local_a = min_bound + my_rank * local_steps * step_size
    local_b = local_a + local_steps * step_size
    local_result = trapezoid_method(math.cos, local_a, local_b, local_steps)

    if my_rank == 0:
        total_result = local_result
        for i in range(1, size):
            total_result += api_comm.recv(source=i)
        return total_result
    api_comm.send(local_result, dest=0)
    return None

def parse_arguments():
    """
    Parse command-line arguments for numerical integration.
    """
    parser = argparse.ArgumentParser(description='Parallel trapezoidal integration using MPI')
    parser.add_argument('-a', type=float, required=True, help='Lower bound of integration')
    parser.add_argument('-b', type=float, required=True, help='Upper bound of integration')
    parser.add_argument('-n', type=int, required=True, help='Number of steps for the trapezoid method')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    min_value = args.a
    max_value = args.b
    my_steps = args.n

    result = parallel_trapezoid(min_value, max_value, my_steps)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        exact_result = exact_integral(min_value, max_value)
        error = abs(exact_result - result)
        print(f"n={my_steps}, error={error}")
