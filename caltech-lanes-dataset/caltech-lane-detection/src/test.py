import IPM
import numpy as np
# image shape: 640 * 480
x = np.array([100, 200], dtype = np.int32)
y = np.array([300, 400], dtype = np.int32)
IPM.points_image2ground(x, y)
print x
print y