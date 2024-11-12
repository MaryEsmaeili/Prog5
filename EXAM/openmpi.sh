#!/bin/bash

# Define the range of workers and output files for timing data
workers=(2 3 4 5 6 7 8)
async_times="async_times.txt"
original_times="original_times.txt"

> $async_times
> $original_times

# Run for each worker count
for n in "${workers[@]}"; do
    echo "Running with $n workers..."

    # Run the asynchronous version and capture time
    async_time=$(/usr/bin/time -f "%e" mpirun -np $n python /homes/mesmaeili/Documents/Prog5/EXAM/MPI_async.py 2>&1 | tail -n 1)
    echo "$n $async_time" >> $async_times

    # Run the original version (assignment2.py) and capture time
    original_time=$(/usr/bin/time -f "%e" mpirun -np $n python /homes/mesmaeili/Documents/Prog5/assignment2.py 2>&1 | tail -n 1)
    echo "$n $original_time" >> $original_times
done

echo "Timing complete. Results saved to $async_times and $original_times."
