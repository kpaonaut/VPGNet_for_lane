import IPM
import numpy as np
# image shape: 640 * 480
import cv2
import time
import os

import adjust_line

def concatenate():
    for i in range(335):
        img0 = cv2.imread("unity/%d.png"%i)
        img1 = cv2.imread("unity/output/driver_%d.png"%i)
        img2 = cv2.imread("unity/output/inversed_%d.png"%i)
        img3 = np.concatenate((img0, img2), axis=1)
        img4 = np.concatenate((img3, img1), axis=1)
        img4 = cv2.resize(img4, (640, 160))
        cv2.imwrite("unity/output%d.png"%i, img4)


def file_organize():
    os.chdir('unity/HDMap_demo')
    bad_cases = [11,15,17,24,46,47,52,58,64,70,71,89,101,109,110,111,118,120,
                 134,152,187,217,227,230,231,244,248,252,256,263,266,267,269,280,284,292,294,305,321,322,328]
    edge_cases = [80,88,93,132,150,262,286]
    os.system('mkdir bad_cases')
    for c in bad_cases:
        os.system('mv output%d.png bad_cases'%c)
    os.system('mkdir edge_cases')
    for c in edge_cases:
        os.system('mv output%d.png edge_cases'%c)

def video_organize():
    os.chdir('VPG_log/log')
    os.system('mkdir raw')
    for i in range(232):
        os.system('mv %d_raw.png raw'%i)


if __name__ == '__main__':
    #concatenate()
    #file_organize()
    video_organize()