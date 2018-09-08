import IPM
import numpy as np
# image shape: 640 * 480
import cv2
import time

import adjust_line

img = cv2.imread("input.png")
tmp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
tmp = np.array(tmp, dtype = np.int32)
line = np.array([[1,1,1],[1,1,1]], dtype = np.int32)
adjust_line.adjust(line, 1, 1, 1, tmp)
print line