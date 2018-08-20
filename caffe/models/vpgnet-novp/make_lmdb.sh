# Declare $PATH_TO_DATASET_DIR and $PATH_TO_DATASET_LIST
PATH_TO_DATASET_DIR="/home/rui/VPGNet/caltech-lanes-dataset/train"
PATH_TO_DATASET_LIST="/home/rui/VPGNet/caltech-lanes-dataset/train/combined_labels.txt"
#PATH_TO_DATASET_DIR="/home/rui/VPGNet/caltech-lanes-dataset"
#PATH_TO_DATASET_LIST="/home/rui/VPGNet/caltech-lanes-dataset/cordova1.txt"

rm -rf LMDB_test
rm -rf LMDB_train
../../build/tools/convert_driving_data $PATH_TO_DATASET_DIR $PATH_TO_DATASET_LIST /home/rui/VPGNet/caffe/models/vpgnet-novp/LMDB_train
../../build/tools/compute_driving_mean /home/rui/VPGNet/caffe/models/vpgnet-novp/LMDB_train ./driving_mean_train.binaryproto lmdb
../../build/tools/convert_driving_data $PATH_TO_DATASET_DIR $PATH_TO_DATASET_LIST /home/rui/VPGNet/caffe/models/vpgnet-novp/LMDB_test
