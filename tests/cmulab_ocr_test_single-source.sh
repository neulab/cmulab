#!/bin/bash -i

[[ $# -ne 4 ]] && { echo "Usage: $0 test_file.txt model_dir/ output_folder/ log_file"; exit 1; }

test_src=$(readlink -ve $1) || exit 1
expt_folder=$(readlink -ve $2) || exit 1
output_folder=$(readlink -ve $3) || exit 1
log_file=$4

mkdir -p $(dirname $log_file)
mkdir -p $output_folder

cd $(dirname $0)


# Set test source file (test_tgt is optional, can be used to compute CER and WER of the predicted output)
#test_src="sample_dataset/postcorrection/training/test_src1.txt"

dynet_mem=1000 # Memory in MB available for testing

params="--pretrain_dec --pretrain_s2s --pretrain_enc --pointer_gen --coverage --diag_loss 2"
trained_model_name="my_trained_model"

# ------------------------------END: Required experimental settings------------------------------


eval $(conda shell.bash hook)
conda activate ocr-post-correction
source activate ocr-post-correction
set -x

{

    # Load the trained model and get the predicted output on the test set (add --dynet-gpu for using GPU)
    python postcorrection/multisource_wrapper.py \
    --dynet-mem $dynet_mem \
    --dynet-autobatch 1 \
    --test_src1 $test_src \
    $params \
    --single \
    --vocab_folder $expt_folder/vocab \
    --output_folder $output_folder \
    --load_model $expt_folder"/models/"$trained_model_name \
    --testing

    echo "Job completed!"

} 2>&1 | tee $log_file
