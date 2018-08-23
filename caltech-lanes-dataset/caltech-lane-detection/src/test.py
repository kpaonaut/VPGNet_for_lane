import IPM
import numpy as np
# image shape: 640 * 480
x = np.array([320, 320, 320, 320], dtype = np.int32)
y = np.array([200, 230, 250, 300], dtype = np.int32)
step = IPM.points_image2ground(x, y)
print x
print y
print step.step_x
print step.step_y