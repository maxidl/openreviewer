#! /bin/bash
# command to run on 1x 80GB A100
DEBUG=0 EXTRACT_IMAGES=0 INFERENCE_RAM=78 VRAM_PER_TASK=5 python marker_bulk_convert.py test_pdfs test_pdfs_marker --workers 15



# # command to run on 4x 80GB A100
# gpus_per_node=4
# num_chunks=4
# start_chunk=0
# for (( i=0; i<gpus_per_node; i++ ))
# do
#     chunk=$(($start_chunk + $i))
#     echo "chunk="$chunk
#     CUDA_VISIBLE_DEVICES=$i DEBUG=0 EXTRACT_IMAGES=0 INFERENCE_RAM=78 VRAM_PER_TASK=5 python marker_bulk_convert.py test_pdfs test_pdfs_marker --workers 15 --chunk_idx $chunk --num_chunks $num_chunks &
# done
# wait




# # command to run on 8 x 4x 80GB A100 nodes with slurm. Change according to your cluster specs.
# #!/bin/bash
# #SBATCH --array=1-8%1
# #SBATCH --partition=
# #SBATCH --gres=gpu:A100:4
# #SBATCH --cpus-per-task=32
# #SBATCH --output=%x-%j.out
# #SBATCH --error=%x-%j.out

# source ~/.bashrc
# conda activate arena-pdf2md
# gpus_per_node=4
# num_chunks=4
# echo "SLURM_ARRAY_TASK_ID="$SLURM_ARRAY_TASK_ID
# start_chunk=$((gpus_per_node*(SLURM_ARRAY_TASK_ID-1)))
# for (( i=0; i<gpus_per_node; i++ ))
# do
#     chunk=$(($start_chunk + $i))
#     echo "chunk="$chunk
#     CUDA_VISIBLE_DEVICES=$i DEBUG=0 EXTRACT_IMAGES=0 INFERENCE_RAM=78 VRAM_PER_TASK=5 python marker_bulk_convert.py pdfs pdfs_marker --workers 15 --chunk_idx $chunk --num_chunks $num_chunks &
# done
# wait