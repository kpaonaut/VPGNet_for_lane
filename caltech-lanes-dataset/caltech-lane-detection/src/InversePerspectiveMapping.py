void points_image2ground(int points_x[], int points_y[], int n){ // n is the number of points

    LaneDetector::CameraInfo *cameraInfo = new LaneDetector::CameraInfo();
    LaneDetector::IPMInfo ipmInfo;
    int ipmWidth = 640; // default, to be changed by parse_config function
    int ipmHeight = 480;
    string filename = "camera.conf";
    parse_config(filename, ipmWidth, ipmHeight, cameraInfo, ipmInfo);

    // FLOAT_MAT_ELEM_TYPE uv[] = {pt1.x, pt2.x, pt1.y, pt2.y};
    FLOAT_MAT_ELEM_TYPE uv[2 * n];
    for (int i = 0; i < n; i ++)
    {
        uv[i] = points_x[i]; // change the format of points!
        uv[2 * i + 1] = points_y[i];
    }
    CvMat uv_cvmat = cvMat(2, n, FLOAT_MAT_TYPE, uv);
    CvMat * xy = cvCreateMat(2, 1, FLOAT_MAT_TYPE);
    CvMat xy_cvmat = *xy;
    mcvTransformImage2Ground(&uv_cvmat, &xy_cvmat, cameraInfo);
    for (int i = 0; i < n; i ++)
    {
        int x = CV_MAT_ELEM(xy_cvmat, float, 0, i);
        int y = CV_MAT_ELEM(xy_cvmat, float, 1, i);
    }
    return;
}

void mcvTransformImage2Ground(const CvMat *inPoints,
                              CvMat *outPoints, const CameraInfo *cameraInfo)
{

  //add two rows to the input points
  CvMat *inPoints4 = cvCreateMat(inPoints->rows+2, inPoints->cols,
      cvGetElemType(inPoints));

  //copy inPoints to first two rows
  CvMat inPoints2, inPoints3, inPointsr4, inPointsr3;
  cvGetRows(inPoints4, &inPoints2, 0, 2);
  cvGetRows(inPoints4, &inPoints3, 0, 3);
  cvGetRow(inPoints4, &inPointsr3, 2);
  cvGetRow(inPoints4, &inPointsr4, 3);
  cvSet(&inPointsr3, cvRealScalar(1));
  //cout<<"inPoints3 "<<CV_MAT_ELEM(inPoints3, float, 0, 0)<<" "<<CV_MAT_ELEM(inPoints3, float, 1, 0)<<endl; // Rui
  cvCopy(inPoints, &inPoints2);
  //cout<<"inPoints3 "<<CV_MAT_ELEM(inPoints3, float, 0, 0)<<" "<<CV_MAT_ELEM(inPoints3, float, 1, 0)<<endl; // Rui
  //create the transformation matrix
  float c1 = cos(cameraInfo->pitch);
  float s1 = sin(cameraInfo->pitch);
  float c2 = cos(cameraInfo->yaw);
  float s2 = sin(cameraInfo->yaw);
  float matp[] = {
    -cameraInfo->cameraHeight*c2/cameraInfo->focalLength.x,
    cameraInfo->cameraHeight*s1*s2/cameraInfo->focalLength.y,
    (cameraInfo->cameraHeight*c2*cameraInfo->opticalCenter.x/
      cameraInfo->focalLength.x)-
      (cameraInfo->cameraHeight *s1*s2* cameraInfo->opticalCenter.y/
      cameraInfo->focalLength.y) - cameraInfo->cameraHeight *c1*s2,

    cameraInfo->cameraHeight *s2 /cameraInfo->focalLength.x,
    cameraInfo->cameraHeight *s1*c2 /cameraInfo->focalLength.y,
    (-cameraInfo->cameraHeight *s2* cameraInfo->opticalCenter.x
      /cameraInfo->focalLength.x)-(cameraInfo->cameraHeight *s1*c2*
      cameraInfo->opticalCenter.y /cameraInfo->focalLength.y) -
      cameraInfo->cameraHeight *c1*c2,

    0,
    cameraInfo->cameraHeight *c1 /cameraInfo->focalLength.y,
    (-cameraInfo->cameraHeight *c1* cameraInfo->opticalCenter.y /
      cameraInfo->focalLength.y) + cameraInfo->cameraHeight *s1,

    0,
    -c1 /cameraInfo->focalLength.y,
    (c1* cameraInfo->opticalCenter.y /cameraInfo->focalLength.y) - s1,
  };
  CvMat mat = cvMat(4, 3, CV_32FC1, matp);
  //multiply
  cvMatMul(&mat, &inPoints3, inPoints4);
  //divide by last row of inPoints4
  for (int i=0; i<inPoints->cols; i++)
  {
    float div = CV_MAT_ELEM(inPointsr4, float, 0, i);
    CV_MAT_ELEM(*inPoints4, float, 0, i) =
        CV_MAT_ELEM(*inPoints4, float, 0, i) / div ;
    CV_MAT_ELEM(*inPoints4, float, 1, i) =
        CV_MAT_ELEM(*inPoints4, float, 1, i) / div;
  }
  //put back the result into outPoints
  cvCopy(&inPoints2, outPoints);
  //clear
  cvReleaseMat(&inPoints4);
}
