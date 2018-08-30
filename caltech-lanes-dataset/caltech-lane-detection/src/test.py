import IPM
import numpy as np
# image shape: 640 * 480
import cv2

img = cv2.imread("lifeng/2.png")
img = cv2.resize(img, (640, 480))
cv2.circle(img, (320, 257), 10, (0, 0, 255))
cv2.imwrite("lifeng/1_vp.png", img)