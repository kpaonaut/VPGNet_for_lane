import numpy as np
import cv2
import math
import time

def adjust(k, b, y_size, x_size, img, downscale):
    """
    With a good initial guess, adjust the extracted lane lines along the way to the middle of the lane-marking
    """

    # line function: y = kx + b

    def update_step(dx_new, dy_new, x, y, line, dx, dy, length, theta_old, x0, y0):
        """
        update the direction of the line along the way. update dx, dy.
        """
        dl_new = math.sqrt(dx_new ** 2.0 + dy_new ** 2.0)
        dx_new /= dl_new
        dy_new /= dl_new
        theta_new = math.atan2(dx_new, dy_new)
        line.append((x, y))
        x0 = x
        y0 = y
        length = 0
        return dx, dy, length, theta_old, x0, y0, line

    # cdef (int, int) xy
    # cdef list line = []
    line = []
    if (k < 0) and (b < y_size - 1):
        x0 = 0
        y0 = int(b)
    elif (k > 0) and (k * (x_size - 1) + b < y_size - 1):
        x0 = x_size - 1
        y0 = int(k * (x_size - 1) + b)
    else:
        y0 = y_size - 1
        x0 = int((y0 - b) / k)
    x, y = x0, y0 # x, y starts from intercepts at the bottom of the image

    length = 0
    dy = - abs(k / math.sqrt(1 + k**2.0))
    dx = dy / (k / math.sqrt(1 + k**2.0)) * 1.0 / math.sqrt(1 + k**2)
    step = 0
    all_step = 0
    while ((img[y, x] == 0) or (step < 2)) and \
        all_step < max(y_size * abs(x - x_size // 2) // (x_size // 2), y_size // 10):

        length += 1
        x = x0 + int(length * dx)
        y = y0 + int(length * dy)
        if img[y, x] == 255: step += 1
        all_step += 1

    time1 = time.time()
    x0 = x
    y0 = y
    l = x
    r = x
    while (img[y, l] == 255) and l > 0: l -= 1
    while (img[y, r] == 255) and r < x_size - 1: r += 1
    x = (l + r) / 2
    length = 0
    if img[y, x] == 255:
        line.append((x, y)) # found the first point *on* the lane marking
        already_white = True # maintain current step status: on a white lane marking or in a space
        white_entrance = (x, y) # record where the line enters the current white marking
    else:
        already_white = False
    theta_old = math.atan2(dy, dx)

    time1 = time.time()
    # the 0.4, 0.6, 0.4 are define the mask we are applying
    # has to be lower than vanishing point, or the ipm'ed polyline's end point will be negative
    while (x > 0) and (x < x_size - 1) and \
          (y > 0.05 * y_size or (x > 0.45 * x_size and x < 0.55 * x_size)): # ( (x < int(x_size * 0.3)) or (x > int(x_size * 0.7)) or (y > int(0.45 * y_size)) ):
        length += 5 * downscale
        while True:
            x = x0 + int(length * dx)
            y = y0 + int(length * dy)
            if x < 0 or x > x_size - 1 or y < 0 or y > y_size - 1:
                break
            if y != y0: # make sure the line is progressing instead of stuck due to small slope
                break
            else:
                length += 5
        if x < 0 or x > x_size - 1 or y < 0 or y > y_size - 1:
            length -= 20
            x = x0 + int(length * dx)
            y = y0 + int(length * dy)
            line.append((x, y))
            break

        if x < x_size - 1 and x > 0 and y > 0 and y < y_size - 1:
            if img[y, x] == 255:
                if not already_white:
                    already_white = True # maintain current step status: on a white lane marking or in a space
                    white_entrance = (x, y)
                l = x
                r = x
                while img[y, l] == 255 and l > 0: l -= 1
                while img[y, r] == 255 and r < x_size - 1: r += 1
                if (abs(((l + r) / 2) - x) > (r - l) / 5) and abs(dy) > 0.01: # if the deviation is too large from the center of the lane marker
                # if dy < 0.05, the line is too flat. will not adjust x to middle
                    x = (l + r) / 2
                    dx_new = (x - x0)
                    dy_new = (y - y0)
                    dx, dy, length, theta_old, x0, y0, line = update_step(dx_new, dy_new, x, y, line, dx, dy, length, theta_old, x0, y0)
                else:
                    line.append((x, y))
            else:
                l = x
                r = x
                step_l = 0
                while img[y, l] == 0 and l > 0 and step_l < 10 * downscale:
                    l -= 1
                    step_l += 1
                    if img[y, l] == 255: break
                step_r = 0
                while img[y, r] == 0 and r < x_size - 1 and step_r < 10 * downscale:
                    r += 1
                    step_r += 1
                    if img[y, r] == 255: break
                if img[y, r] == 0 and img[y, l] == 0: # there is a space here!
                    continue
                    if already_white:
                        already_white = False
                        dx_new = (x - white_entrance[0])
                        dy_new = (y - white_entrance[1])
                        dx, dy, length, theta_old, x0, y0, line = update_step(dx_new, dy_new, x, y, line, dx, dy, length, theta_old, x0, y0)
                else:
                    if img[y, r] == 255:
                        l = r
                    else:
                        r = l
                    while img[y, l] == 255 and l > 0: l -= 1
                    while img[y, r] == 255 and r < x_size - 1: r += 1
                    x = (l + r) / 2
                    dx_new = (x - x0)
                    dy_new = (y - y0)
                    dx, dy, length, theta_old, x0, y0, line = update_step(dx_new, dy_new, x, y, line, dx, dy, length, theta_old, x0, y0)
                    
    time2 = time.time()
    print "ADJUST TIMEEEEEEEEE", time2 - time1
    return line