import argparse
import numpy as np
import math

# The exact value of the integral
def exact_integral(lower_bound, upper_bound):
    return math.sin(upper_bound) - math.sin(lower_bound)

# Trapezoidal rule implementation
def trapezoid_method(func, lower_bound, upper_bound, n):
    h = (upper_bound - lower_bound) / n
    total = 0.5 * (func(lower_bound) + func(upper_bound))
    
    for i in range(1, n):
        total += func(lower_bound + i * h)
    
    return total * h

# Parse arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Numerical integration using trapezoid method')
    parser.add_argument('-a', type=float, required=True, help='Lower bound of integration')
    parser.add_argument('-b', type=float, required=True, help='Upper bound of integration')
    parser.add_argument('-n', type=int, required=True, help='Number of steps for the trapezoid method')
    
    return parser.parse_args()

# Main
if __name__ == "__main__":
    args = parse_arguments()
    
    # Bounds and number of steps
    lower_bound = args.a
    upper_bound = args.b
    n = args.n
    
    # Choose the function to integrate
    func = math.cos
    
    # Numerical integral using the trapezoidal rule
    numerical_result = trapezoid_method(func, lower_bound, upper_bound, n)
    
    # Exact integral value
    exact_result = exact_integral(lower_bound, upper_bound)
    
    # Error
    error = abs(exact_result - numerical_result)
    
    print(f"{n},{error}")
