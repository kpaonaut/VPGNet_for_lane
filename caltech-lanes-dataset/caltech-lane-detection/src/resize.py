import cv2
import numpy as np

img = cv2.imread("1.png")
img = cv2.resize(img, (640, 480))
cv2.imwrite("1.png", img)
cv2.imwrite("2.png", img)
cv2.imwrite("input.png", img)