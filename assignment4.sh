#!/bin/bash
#SBATCH --job-name=assignment4
#SBATCH --output=output_assignment4.txt
#SBATCH --error=error_assignment4.txt
#SBATCH --time=02:00:00      
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=assemblix  # Specify the assemblix partition

# Run the Python script
python3 assignment4.py


