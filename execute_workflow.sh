cd caffe/models/vpgnet-novp/script-rui/
python run_model.py
python post_process.py
cp thresholded.png ~/Lane_perception
cd ~/Lane_perception
mv thresholded.png 1.png
cp 1.png 2.png
python lane_extension_polyline_for_VPG.py
cd ~/VPGNet/caltech-lanes-dataset/caltech-lane-detection/src
./a
cd ~/VPGNet