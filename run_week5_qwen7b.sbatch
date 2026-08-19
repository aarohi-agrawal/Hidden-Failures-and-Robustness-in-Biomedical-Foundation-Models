#!/bin/bash
#SBATCH --job-name=week5-qwen7b
#SBATCH --partition=gpu-preempt
#SBATCH --time=02:00:00
#SBATCH --gpus=1
#SBATCH --mem=32G
#SBATCH --output=outputs/logs/week5_qwen7b_%j.out
#SBATCH --error=outputs/logs/week5_qwen7b_%j.err

cd ~/Hidden-Failures-and-Robustness-in-Biomedical-Foundation-Models

source .venv/bin/activate

echo "Starting Week 5 Qwen 7B run"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
date

python src/adapters/run_mmvp_week5.py \
  --manifest data/manifests/week5_evidence_ladder_eval.csv \
  --questions data/Questions.csv \
  --output outputs/raw/week5_qwen7b_full.jsonl \
  --model Qwen/Qwen2.5-VL-7B-Instruct \
  --model-revision main \
  --start 16 \
  --limit 184

echo "Job finished"
date
