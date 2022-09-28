#!/bin/bash -i

[[ $# -ne 5 ]] && { echo "Usage: $0 src1_data.zip tgt_data.zip unlabeled_data.zip working_dir/ log_file"; exit 1; }

src1_data=$(readlink -ve $1) || exit 1
tgt_data=$(readlink -ve $2) || exit 1
unlabeled_data=$(readlink -ve $3) || exit 1
working_dir=$(readlink -ve $4) || exit 1
log_file=$(readlink -m $5)


cd $(dirname $0)


# Set experiment parameters

dynet_mem=3000 # Memory in MB available for training

params="--pretrain_dec --pretrain_s2s --pretrain_enc --pointer_gen --coverage --diag_loss 2"
pretrained_model_name="my_pretrained_model"
trained_model_name="my_trained_model"

# ------------------------------END: Required experimental settings------------------------------


mkdir -p $(dirname $log_file)


exit_code=1

eval $(conda shell.bash hook)
conda activate ocr-post-correction
#source activate ocr-post-correction
set -x

{

    annotated_dir=${working_dir}/text_outputs/corrected/
    mkdir -p ${annotated_dir}/src1 ${annotated_dir}/tgt
    (cd ${annotated_dir}/src1; unzip -j $src1_data)
    (cd ${annotated_dir}/tgt; unzip -j $tgt_data)

    unannotated_src=${working_dir}/text_outputs/uncorrected/src1/
    mkdir -p $unannotated_src
    (cd $unannotated_src; unzip -j $unlabeled_data)

    # Create experiment directories
    expt_folder=${working_dir}/expt/
    mkdir -p $expt_folder
    mkdir $expt_folder/debug_outputs
    mkdir $expt_folder/models
    mkdir $expt_folder/outputs
    mkdir $expt_folder/pretrain_logs
    mkdir $expt_folder/pretrain_models
    mkdir $expt_folder/train_logs
    mkdir $expt_folder/vocab

    python -u utils/prepare_data.py  \
	--unannotated_src1 $unannotated_src  \
	--annotated_src1 ${annotated_dir}/src1/  \
	--annotated_tgt ${annotated_dir}/tgt/  \
	--output_folder ${working_dir}/postcorrection/


    # Set pretraining, training and development set files
    pretrain_src="${working_dir}/postcorrection/pretraining/pretrain_src1.txt"
    train_src="${working_dir}/postcorrection/training/train_src1.txt"
    train_tgt="${working_dir}/postcorrection/training/train_tgt.txt"
    dev_src="${working_dir}/postcorrection/training/dev_src1.txt"
    dev_tgt="${working_dir}/postcorrection/training/dev_tgt.txt"


    # Denoise outputs for pretraining
    python -u utils/denoise_outputs.py \
    --train_src1 $train_src \
    --train_tgt $train_tgt \
    --input $pretrain_src \
    --output $pretrain_src'.denoised'

    pretrain_tgt=$pretrain_src'.denoised'


    # Create character vocabulary for the post-correction model
    python -u postcorrection/create_vocab.py \
    --src1_files $train_src $dev_src \
    --tgt_files $train_tgt $dev_tgt \
    --output_folder $expt_folder/vocab/


    # Pretrain the model (add --dynet-gpu for using GPU)
    # See postcorrection/opts.py for all the options
    python -u postcorrection/multisource_wrapper.py \
    --dynet-mem $dynet_mem \
    --dynet-autobatch 1 \
    --pretrain_src1 $pretrain_src \
    --pretrain_tgt $pretrain_tgt \
    $params \
    --single \
    --vocab_folder $expt_folder/vocab/ \
    --output_folder $expt_folder/ \
    --model_name $pretrained_model_name \
    --pretrain_only

    # Load the pretrained model and train the model using manually annotated training data (add --dynet-gpu for using GPU)
    # See postcorrection/opts.py for all the options
    python -u postcorrection/multisource_wrapper.py \
    --dynet-mem $dynet_mem \
    --dynet-autobatch 1 \
    --train_src1 $train_src \
    --train_tgt $train_tgt \
    --dev_src1 $dev_src \
    --dev_tgt $dev_tgt \
    $params \
    --single \
    --vocab_folder $expt_folder/vocab/ \
    --output_folder $expt_folder/ \
    --load_model $expt_folder"/pretrain_models/"$pretrained_model_name \
    --model_name $trained_model_name \
    --train_only

    if [ -s ${expt_folder}/models/${trained_model_name} ]; then
        echo "Traning completed successfully!"
        exit_code=0
    else
        echo "Traning failed!"
        exit_code=1
    fi

} 2>&1 | tee $log_file

exit $exit_code