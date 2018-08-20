/***
Created by Rui Wang @ Tsinghua University
08/14/2018
-This file utilizes caltech dataset and performs Inverse Perspective Mapping on it
-usage:
input.png(RGB) -> IPM according to configs -> output.png(gray scale image)

--NOTICE:
to compile the project use the following command:
g++ IPM.cpp InversePerspectiveMapping.cc mcv.cc -o a `pkg-config --libs opencv`
***/

#include <opencv2/opencv.hpp>
#include <list>
#include <vector>
#include "InversePerspectiveMapping.hh"
#include "mcv.hh"

using namespace std;
using namespace cv;

int main(){

    Mat image = imread("input.png");
    Mat gray_img;
    cvtColor(image, gray_img, COLOR_BGR2GRAY);
    CvMat converted_img = CvMat(gray_img);
    CvMat *int_image = &converted_img;
    CvMat *inImage = cvCreateMat(int_image->height, int_image->width, FLOAT_MAT_TYPE);
    cvConvertScale(int_image, inImage, 1./255);

    Mat output_img = cvarrToMat(&converted_img);
    imwrite("gray.png", output_img);

    // sizes: the output size, can be arbitrary
    int ipmWidth = 640; //160; // 160 by default
    int ipmHeight = 480; //120; // 120 by default
    CvMat * ipm = cvCreateMat(ipmHeight, ipmWidth, inImage->type);

    // IPM info: define the pixel range
    LaneDetector::IPMInfo ipmInfo;
    ipmInfo.vpPortion = .05; // how far is the image top from vanishing point (bc vp is too far, can't display all)
    ipmInfo.ipmLeft = 85;
    ipmInfo.ipmRight = 550;
    ipmInfo.ipmTop = 50;
    ipmInfo.ipmBottom = 480;// 380;
    ipmInfo.ipmInterpolation = 0;

    list<CvPoint> outPixels;

    LaneDetector::CameraInfo *cameraInfo = new LaneDetector::CameraInfo();
    // focal length
    float focalLengthX = 309.4362;
    float focalLengthY = 344.2161;
    cameraInfo->focalLength = cvPoint2D32f(focalLengthX, focalLengthY);
    // optical center coordinates in image frame (origin is (0,0) at top left)
    float opticalCenterX = 317.9034;
    float opticalCenterY = 256.5352;
    cameraInfo->opticalCenter = cvPoint2D32f(opticalCenterX, opticalCenterY);
    // height of the camera in mm
    cameraInfo->cameraHeight = 2179.8; //# 393.7 + 1786.1
    // pitch of the camera
    cameraInfo->pitch = 14.0 * CV_PI / 180.0; // in radius!
    // yaw of the camera
    cameraInfo->yaw  = 0.0 * CV_PI / 180.0;
    // imag width and height
    cameraInfo->imageWidth = 640;
    cameraInfo->imageHeight = 480;

    // execute GetIPM, new image is ipm
    list<CvPoint>* out_pt = &outPixels;
    LaneDetector::mcvGetIPM(inImage, ipm, &ipmInfo, cameraInfo);
    printf("Press any key to continue!\n");
    LaneDetector::SHOW_IMAGE(ipm, "IPM_image");
    cvConvertScale(ipm, ipm, 255);
    output_img = cvarrToMat(ipm);
    cv::imwrite("output.png", output_img);

    return 0;
}
