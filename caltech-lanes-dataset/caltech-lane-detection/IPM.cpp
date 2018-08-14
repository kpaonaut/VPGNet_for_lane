#include <opencv2/opencv.hpp>
#include <list>
#include <vector>
#include "src/InversePerspectiveMapping.hh"

using namespace std;
using namespace cv;

int main(){

    Mat image = imread("input.png");
    CvMat converted_img = CvMat(image);
    CvMat *inImage = &converted_img;

    // LaneDetectorConf *stopLineConf;

    // init stopLineConf
    // in LaneDetector.cc
    // mcvInitLaneDetectorConf("Stoplines.conf", // stopLineConf config file
    //     stopLineConf)

    // ipmVpPortion = .2//#.075#0.1 #.05
    // ipmLeft = 85
    // ipmRight = 550
    // ipmTop = 50
    // ipmBottom = 380 #350 #300 for latest St-lukes data
    // ipmInterpolation = 0;
    int ipmWidth = 160;
    int ipmHeight = 120;

    CvMat * ipm;
    ipm = cvCreateMat(ipmHeight, ipmWidth, inImage->type);

    LaneDetector::IPMInfo ipmInfo;
    ipmInfo.vpPortion = .2;
    ipmInfo.ipmLeft = 85;
    ipmInfo.ipmRight = 550;
    ipmInfo.ipmTop = 50;
    ipmInfo.ipmBottom = 380;
    ipmInfo.ipmInterpolation = 0;

    list<CvPoint> outPixels;

    LaneDetector::CameraInfo *cameraInfo;
    // focal length
    float focalLengthX = 309.4362;
    float focalLengthY = 344.2161;
    cameraInfo->focalLength = FLOAT_POINT2D(focalLengthX, focalLengthY);
    // optical center coordinates in image frame (origin is (0,0) at top left)
    float opticalCenterX = 317.9034;
    float opticalCenterY = 256.5352;
    cameraInfo->opticalCenter = FLOAT_POINT2D(opticalCenterX, opticalCenterY);
    // height of the camera in mm
    cameraInfo->cameraHeight = 2179.8; //# 393.7 + 1786.1
    // pitch of the camera
    cameraInfo->pitch = 14.0;
    // yaw of the camera
    cameraInfo->yaw  = 0.0;
    // imag width and height
    cameraInfo->imageWidth = 640;
    cameraInfo->imageHeight = 480;

    // execute GetIPM, new image is ipm
    LaneDetector::mcvGetIPM(inImage, ipm, &ipmInfo, cameraInfo, &outPixels);
    Mat output_img = cvarrToMat(ipm);
    cv::imwrite("output.png", output_img);

    return 0;
}
