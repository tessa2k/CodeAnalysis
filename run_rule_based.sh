#!/bin/bash
#SBATCH --mem=10G                    # Request 10 GiB of memory
#SBATCH --time=12:00:00               # Set a maximum runtime of 6 hours
#SBATCH --output=logs/rule_based_%j.out  # Save standard output to log file
#SBATCH --error=logs/rule_based_%j.err   # Save error output to log file

# Run the Python script
python rule_based/run.py --data_folder "../2022_Data" --batch --batch_size 20

# Optional: Print job finish time
echo "Job finished at $(date)"
