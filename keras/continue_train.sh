#!/bin/bash
# copy host version of inception wrights to avoid downloading again
mkdir -p ~/.keras/models
cp /git/visnavml/keras/inception_v3_weights_tf_dim_ordering_tf_kernels_notop.h5 ~/.keras/models/
# run multi_gpu training
TRAIN_DIR="/data/training_data_balanced/benthoz_ziggy_299patch_split90-10/training/"
VAL_DIR="/data/training_data_balanced/benthoz_ziggy_299patch_split90-10/validation/"
INPUT_MODEL="/data/inception_kelp_nokelp.model"
OUTPUT_MODEL="/data/inception_kelp_nokelp_continue.model"
python K2_transfer_inception_V3_multigpu_continue.py --train_dir $TRAIN_DIR --val_dir $VAL_DIR  --output_model_file $OUTPUT_MODEL --input_model_file $INPUT_MODEL
