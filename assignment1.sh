#!/bin/bash

#SBATCH --job-name=trapezoid_integration
#SBATCH --output=results.csv
#SBATCH --ntasks=1
#SBATCH --time=00:10:00
#SBATCH --mem-per-cpu=1000

module load python/3.11

# Lower and upper bounds of the integral
a=0
b=math.pi/2

output_file="results.csv"

# Header for the output file
echo "n,error" > $output_file

# Loop over different values of n
for n in 10 50 100 500 1000 5000 10000
do
    # Call the python script and append the output to the results file
    python3 assignment1.py -a $a -b $b -n $n >> $output_file
done
