#!/bin/bash
#SBATCH --job-name=assignment4
#SBATCH --output=output.txt
#SBATCH --error=errors.txt
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --ntasks=1

# Load Spark and run the python script
python3 assignment4.py
