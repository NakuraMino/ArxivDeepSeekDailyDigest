#!/bin/bash

source /path/to/conda/bin/activate arxiv
export HF_HOME='/path/to/save/huggingface/models/'
cd /path/to//ArxivDailyDigest/src/daily_digest/ 
python main.py &> /path/to/ArxivDailyDigest/src/daily_digest/logs/out_$(date +\%Y-\%m-\%d).txt
conda deactivate
