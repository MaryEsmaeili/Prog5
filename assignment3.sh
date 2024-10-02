#!/bin/bash
#SBATCH --job-name=pubmed_import
#SBATCH --output=pubmed_import.log
#SBATCH --ntasks=1
#SBATCH --time=00:10:00
#SBATCH --mem=1G

# Load any necessary modules (e.g., Python, MySQL)
module load python/3.8
module load mysql

# Execute the Python script
python3 assignment3.py
