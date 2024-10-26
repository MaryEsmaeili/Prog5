#!/bin/bash

#SBATCH --job-name=mpi_trapezoid            # Job name
#SBATCH --output=results.csv                # Standard output
#SBATCH --partition=assemblix               # Specify the partition
#SBATCH --ntasks=8                          # Request 8 tasks (cores)
#SBATCH --nodes=1                           # Request 1 node (since only 2 are available)
#SBATCH --time=00:20:00                     # Time limit
#SBATCH --mem-per-cpu=1000                  # Memory per CPU

# Activate your Python environment
source ~/my_new_venv/bin/activate

# Disable X11 forwarding
unset DISPLAY

output_file="all_times.txt"
echo "cores,time" > $output_file            # Add a header to the output file

# Set number of integration steps and interval bounds
n=1000000000
a=0
b=1

# Loop over core counts (2, 4, 8, 16)
for cores in 2 4 8 16 32; do
    echo "Running with $cores cores"
    /usr/bin/time -f "$cores,%e" mpirun -np $cores python3 assignment5.py -a $a -b $b -n $n > /dev/null 2>> $output_file
done
