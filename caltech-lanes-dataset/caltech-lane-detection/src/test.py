import IPM
import numpy as np
# image shape: 640 * 480
import cv2
import time

t0 = time.time()
i = 0
a = np.zeros((200, 200))
c = []
while i < 1000:
	b = a[100][100]
	c.append(b)
	i += 1
t1 = time.time()
print t1 - t0