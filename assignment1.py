"""
This module performs numerical integration using the trapezoidal rule.
"""

import math
import argparse

# The exact value of the integral
def exact_integral(l_bound, u_bound):
    """
    Compute the exact integral of cos(x) between l_bound and u_bound.
    
    Parameters:
    l_bound (float): The lower bound of integration.
    u_bound (float): The upper bound of integration.
    
    Returns:
    float: The exact integral value.
    """
    return math.sin(u_bound) - math.sin(l_bound)

# Trapezoidal rule implementation
def trapezoid_method(func, l_bound, u_bound, num_steps):
    """
    Approximate the integral using the trapezoidal rule.

    Parameters:
    func (callable): The function to integrate.
    l_bound (float): The lower bound of the integral.
    u_bound (float): The upper bound of the integral.
    num_steps (int): The number of trapezoids used in the approximation.

    Returns:
    float: The approximate value of the integral.
    """
    step_size = (u_bound - l_bound) / num_steps
    total = 0.5 * (func(l_bound) + func(u_bound))
    for i in range(1, num_steps):
        total += func(l_bound + i * step_size)
    return total * step_size

# Parse arguments
def parse_arguments():
    """
    Parse command-line arguments for the numerical integration script.
    """
    parser = argparse.ArgumentParser(description='Numerical integration using trapezoid method')
    parser.add_argument('-a', type=float, required=True, help='Lower bound of integration')
    parser.add_argument('-b', type=float, required=True, help='Upper bound of integration')
    parser.add_argument('-n', type=int, required=True, help='Number of steps for the trapezoid method')
    return parser.parse_args()

# Main
if __name__ == "__main__":
    args = parse_arguments()
    # Bounds and number of steps
    min_value = args.a
    max_value = args.b
    n_steps = args.n
    # Choose the function to integrate
    my_func = math.cos
    # Numerical integral using the trapezoidal rule
    numerical_result = trapezoid_method(my_func, min_value, max_value, n_steps)
    # Exact integral value
    exact_result = exact_integral(min_value, max_value)
    # Error
    error = abs(exact_result - numerical_result)
    print(f"{n_steps},{error}")
