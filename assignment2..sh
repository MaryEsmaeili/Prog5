#!/bin/bash

#SBATCH --job-name=mpi_trapezoid
#SBATCH --output=results.csv
#SBATCH --ntasks=1
#SBATCH --time=00:20:00
#SBATCH --mem-per-cpu=1000

module load python/3.11 openmpi/4.0.5

output_file="results.csv"
echo "n,workers,time" > $output_file

# Fixed number of steps
n=10000
a=0
b=$(echo "scale=10; 3.14159/2" | bc)

# Loop over number of workers
for workers in {1..32}; do
    # Time the execution with /usr/bin/time
    (/usr/bin/time -f "%e" mpirun -np $workers python3 assignment2.py -a $a -b $b -n $n) 2>> $output_file
done
