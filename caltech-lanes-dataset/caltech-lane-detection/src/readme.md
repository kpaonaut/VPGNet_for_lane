Author Rui Wang, Tsinghua University 08/2018
This package implements inverse perspective mapping (IPM) and general post-processing for lane lines detection.

Package Usage:
To compile just for IPM, run 
~~~
g++ IPM.cpp InversePerspectiveMapping.cc mcv.cc -o a `pkg-config --libs opencv`
~~~
This will generate an executable `a`. Name the picture you want to perform IPM on `input.png`, first resize it (optional, depending on your `camera.conf` file and picture size) using `resize.py` and then run `./a` will give you the output in `output.png`.
To compile for entire post-processing, run `source swig.sh`. This generates the C++-Python interface and allows python to directly call IPM functions.
To run this, make sure _swig_ is properly installed on your computer. The config file for swig is `IPM.i`.
`python HDMap_pp_workflow.py filename` - carry out the entire post-processing workflow on file `filename`.
The main functions are in `lane_extension_polyline_for_MultiNet.py`.
camera parameter configuration for Unity & HD Map:
modify in `IPM.cpp`
camera parameter configuration for general usage (perform IPM on other tasks):
modify in `camera.conf`
**Notice**: In `IPM.cpp`, there are two overloaded functions `parse_config()`. The version which reads from file is slower and can't be used for batch processing since it requires file I/O everytime.

Here is a list of parameters for c++ and python that optimizes the performance for straight line only (withou adjustment):
For `camera.conf`
vpPortion = 0.045
For `houghlines()`
threshold = int(60 * downscale) # the number of votes (voted by random points on the picture)
min_line_length = int(100 * downscale) # line length
For `cluster_lines()`
cluster_threshold = int(2.5 * 3.33 / upscale)
For `cluster_directions()`
cluster_threshold = 5
