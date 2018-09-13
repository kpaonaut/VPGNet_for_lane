import IPM
import numpy as np
# image shape: 640 * 480
import cv2
import time

import adjust_line

for i in range(335):
    img0 = cv2.imread("unity/%d.png"%i)
    img0 = cv2.resize(img0, (640, 480))
    img1 = cv2.imread("unity/output/driver_%d.png"%i)
    img2 = cv2.imread("unity/output/inversed_%d.png"%i)
    img3 = np.concatenate((img0, img2), axis=1)
    img4 = np.concatenate((img3, img1), axis=1)
    cv2.imwrite("unity/output%d.png"%i, img4)