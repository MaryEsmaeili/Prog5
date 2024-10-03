#!/bin/bash
#SBATCH --job-name=pubmed_db
#SBATCH --output=output.txt
#SBATCH --error=error.txt
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G

# Run the Python script
python3 assignment3.py
