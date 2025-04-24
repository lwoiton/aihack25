#!/bin/bash
# Runs the EUROGATE AI Agent API server
source $(conda info --base)/etc/profile.d/conda.sh
conda activate eurogate-ai
python -m app.main
