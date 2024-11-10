#!/bin/bash
#SBATCH --job-name=pubmed_analysis      # Job name
#SBATCH --output=pubmed_analysis.out    # Standard output file
#SBATCH --error=pubmed_analysis.err     # Standard error file
#SBATCH --ntasks=1                      # Number of tasks (typically 1 for Spark jobs)
#SBATCH --cpus-per-task=16              # Number of CPUs per task (adjust as needed)
#SBATCH --mem=64G                       # Memory per node (adjust as needed)
#SBATCH --time=24:00:00                 # Time limit for the job (24 hours in this case)
#SBATCH --partition=general             # Partition to submit to (adjust based on availability)

# Load the necessary modules (system should already have necessary libraries)
# For this case, Spark should be available by default; hence, we don't load any extra modules.

# Specify the directory and input file
PUBMED_FILE="/data/datasets/NCBI/PubMed/pubmed21n0562.xml"

# Run the Python script with the given input file
python3 assignment4.py $PUBMED_FILE
