# VPGNet Usage and Lane Detection

Rui Wang @ Tsinghua University

This project is partially forked from [VPGNet](https://github.com/SeokjuLee/VPGNet). Also check out [caltech lane detection repo](https://github.com/mohamedadaly/caltech-lane-detection).

## Overview
This project modified the VPGNet implementation, with a focus on lane detection. It also made use of and modified the __inverse perspective mapping__ (IPM) from caltech lane detection.

This project aims to develop a clearer document for VPGNet usage, providing a clean interface for lane detection. Hopefully with this document you'll be able to __actually__ run VPGNet without too much pain. It also implements some of the post-processing techniques that are not provided in the original repo. Please check out their original repo referenced above, and cite their paper if it helped your research.

Please see it running in **Usage** section. Apart from the workflow as a whole, it also provides standalone post-processing modules for pictures. You may find some of the implementations here useful, including IPM and lane clustering.

## Installation
The entire repo is tested on Ubuntu 16.04. For other OS, you may need additional information or implement your own modification to make it work. As a quick notice, some of the major dependencies include python, caffe and opencv.

Note that the installation process might be extremely painful without prior experience with Ubuntu and these open source libraries. Nevertheless, I will try to make the tutorial as clear as possible.

## Usage

## Training

## Data Augmentation

## Test
The original

## Inverse Perspective Mapping
There is also a standalone implementation of inverse perspective mapping. Go to `caltech_lanes_dataset/caltech_lane_detection/src/`, and compile it (this is to compile only the IPM, not the entire caltech project!) with
~~~
g++ IPM.cpp InversePerspectiveMapping.cc mcv.cc -o a `pkg-config --libs opencv`
~~~
Here `a` is the executable file. Save the image you want to perform IPM as `input.png` under the same directory, and run `./a`. Now follow any prompts in your command line window. The result will be saved as `output.png`. An example is already included in the folder.

Note, that you will need to change the camera configuration if you are not using caltech lane dataset. The parameters can be set in `IPM.cpp`, whereafter you will have to recompile before running. You should be able to navigate through and modify the project for yourself with **Sublime Text 3** or equivalent editors (as long as it can link the function definition and/or reference).

## Post Processing

## ::::::::::::::::  Supplementary  ::::::::::::::::::
**Below is the original readme file from VPGNet:**
## [VPGNet: Vanishing Point Guided Network for Lane and Road Marking Detection and Recognition]

International Conference on Computer Vision (ICCV) 2017

<img src="./teaser.png" width="400">

In this paper, we propose a unified end-to-end trainable multi-task network that jointly handles lane and road marking detection and recognition that is guided by a vanishing point under adverse weather conditions. We tackle rainy and low illumination conditions, which have not been extensively studied until now due to clear challenges. For example, images taken under rainy days are subject to low illumination, while wet roads cause light reflection and distort the appearance of lane and road markings. At night, color distortion occurs under limited illumination. As a result, no benchmark dataset exists and only a few developed algorithms work under poor weather conditions. To address this shortcoming, we build up a lane and road marking benchmark which consists of about 20,000 images with 17 lane and road marking classes under four different scenarios: no rain, rain, heavy rain, and night. We train and evaluate several versions of the proposed multi-task network and validate the importance of each task. The resulting approach, VPGNet, can detect and classify lanes and road markings, and predict a vanishing point with a single forward pass. Experimental results show that our approach achieves high accuracy and robustness under various conditions in real-time (20 fps). The benchmark and the VPGNet model will be publicly available.


### Supplementary
+ https://www.youtube.com/watch?v=jnewRlt6UbI


### Citation
Please cite [VPGNet](http://openaccess.thecvf.com/content_iccv_2017/html/Lee_VPGNet_Vanishing_Point_ICCV_2017_paper.html) in your publications if it helps your research:

    @InProceedings{Lee_2017_ICCV,
      author = {Lee, Seokju and Kim, Junsik and Shin Yoon, Jae and Shin, Seunghak and Bailo, Oleksandr and Kim, Namil and Lee, Tae-Hee and Seok Hong, Hyun and Han, Seung-Hoon and So Kweon, In},
      title = {VPGNet: Vanishing Point Guided Network for Lane and Road Marking Detection and Recognition},
      booktitle = {The IEEE International Conference on Computer Vision (ICCV)},
      month = {Oct},
      year = {2017}
    }


### Baseline Usage
1) Clone the repository

    ```Shell
    git clone https://github.com/SeokjuLee/VPGNet.git
    ```

2. Prepare dataset from Caltech Lanes Dataset.<br/>
(Our dataset is currently being reviewed by Samsung Research. This baseline doesn't need VP annotations.)
    - Download [Caltech Lanes Dataset](http://www.mohamedaly.info/datasets/caltech-lanes).
    - Organize the file structure as below.
    ```Shell
    |__ VPGNet
        |__ caffe
        |__ caltech-lanes-dataset
            |__ caltech-lane-detection/matlab
            |__ cordova1
            |__ cordova2
            |__ washington1
            |__ washington2
            |__ vpg_annot_v1.m
    ```
    - Generate list files using 'caltech-lanes-dataset/vpg_annot_v1.m'. Arrange training and validation sets as you wish.

3. Caffe compliation
    - Compile our Caffe codes following the [instructions](http://caffe.berkeleyvision.org/installation.html).
    - Move to 'caffe/models/vpgnet-novp'. This is our workspace.

4. Make LMDB
    - Change paths in 'make_lmdb.sh' and run it. The LMDB files would be created.

5. Training
    - Run 'train.sh'


### Dataset Contact
+ All rights about the dataset are preserved by Samsung Electronics Co.
+ Please contact [Tae-Hee Lee](mailto:th810.lee@samsung.com), [Hyun Seok Hong](mailto:hyunseok76.hong@samsung.com), and [Seung-Hoon Han](mailto:luoes.han@samsung.com) with questions and comments.


### Log
+ Sep.11.2017: The "VPGNet" pages beta test
+ Dec.18.2017: Caffe codes uploaded
