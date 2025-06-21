#!/bin/bash

#SBATCH --job-name=finetune
#SBATCH --output=slurm_logs/%x-%j.out
#SBATCH --error=slurm_logs/%x-%j.out
#SBATCH --partition=
#SBATCH --nodes=16                   # number of nodes
#SBATCH --ntasks-per-node=1         # number of MP tasks
#SBATCH --gres=gpu:4                # number of GPUs per node
#SBATCH --cpus-per-task=64         # number of cores per tasks


######################
### Set enviroment ###
######################
export TMPDIR=$LOCAL_TMPDIR
module load cuda
source ~/.bashrc
source activate axolotl
# export WANDB_MODE=offline
# export HF_HUB_OFFLINE=1
# export HF_DATASETS_OFFLINE=1
# export TRANSFORMERS_OFFLINE=1
GPUS_PER_NODE=4
NNODES=$SLURM_NNODES
NUM_PROCESSES=$((NNODES * GPUS_PER_NODE))
echo "NNODES: "$NNODES
echo "NUM_PROCESSES: "$NUM_PROCESSES
######################

######################
#### Set network #####
######################
MASTER_ADDR=$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)
MASTER_PORT=57937
######################
echo "MASTER_ADDR: "$MASTER_ADDR
echo "MASTER_PORT: "$MASTER_PORT

echo "HF_HOME: "$HF_HOME
echo "hf login: "$(huggingface-cli whoami)
#  accelerate launch -m axolotl.cli.train ./config.yml 

# mkdir -p $LOCAL_TMPDIR/.triton/autotune
export TRITON_CACHE_DIR=$LOCAL_TMPDIR
echo "TRITON_CACHE_DIR: "$TRITON_CACHE_DIR

export ACCELERATE_LOG_LEVEL=info
export LAUNCHER="accelerate launch \
    --config_file acc_config.yaml \
    --num_processes $NUM_PROCESSES \
    --num_machines $NNODES \
    --rdzv_backend c10d \
    --main_process_ip $MASTER_ADDR \
    --main_process_port $MASTER_PORT \
    "
export SCRIPT="-m axolotl.cli.train"
export SCRIPT_ARGS="fft-llama31-8B-liger-ds.yaml"
    
# This step is necessary because accelerate launch does not handle multiline arguments properly
export CMD="$LAUNCHER $SCRIPT $SCRIPT_ARGS" 
echo "CMD: "$CMD
srun --output=slurm_logs/%x-%j-%N.out --wait=60 --kill-on-bad-exit=1 --jobid $SLURM_JOB_ID $CMD
