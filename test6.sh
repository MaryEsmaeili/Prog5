#!/bin/bash
#SBATCH --job-name=Prog5_Assignment6
#SBATCH --output=assignment6_output.txt
#SBATCH --error=assignment6_error.txt
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --partition=assemblix

# Activate environment
source ~/Documents/my_new_nenv/bin/activate

# Run Python script
/homes/mesmaeili/Documents/myenv/bin/python3 /homes/mesmaeili/Documents/Prog5/test.py