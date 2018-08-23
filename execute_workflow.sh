cd caffe/models/vpgnet-novp/script-rui/
python run_model.py # 
# python post_process.py
cp workspace/4/mask.png workspace/4/example.png ~/VPGNet/caltech-lanes-dataset/caltech-lane-detection/src
cd ~/VPGNet/caltech-lanes-dataset/caltech-lane-detection/src
mv example.png input.png
mv mask.png 1.png
cp 1.png 2.png
./a
python lane_extension_polyline_for_VPG.py
cd ~/VPGNet