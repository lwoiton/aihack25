#!/bin/bash
# Activates the Conda environment for the EUROGATE AI Agent
source $(conda info --base)/etc/profile.d/conda.sh
conda activate eurogate-ai
echo "EUROGATE AI Agent environment activated."
