# Notice: this program works well for lane output of continuous lines. All parameters are tuned
# for the test data in /lane/lane_test_data/outputForConnectedWideDash
import cv2
import numpy as np
import math
import scipy
from scipy import cluster

# define parameters:
downsample_scale = 0.3 # 0.3 default
cluster_threshold = 20
threshold = 30 # number of votes required to be considered a line, 40 default 
# adjustable params:
# mask geometry
# houghLinesP parms

def check(z, i, n, clustered, checked, clusters, cluster_id):

    if z[i, 0] < n and z[i, 1] < n:
        checked[i] = 1
        clustered[int(z[i, 0])] = 1
        clustered[int(z[i, 1])] = 1
        clusters[cluster_id].append(int(z[i, 0]))
        clusters[cluster_id].append(int(z[i, 1]))
    elif z[i, 0] >= n and z[i, 1] < n:
        checked[i] = 1
        clustered[int(z[i, 1])] = 1
        clusters[cluster_id].append(int(z[i, 1]))
        check(z, int(z[i, 0]) - n, n, clustered, checked, clusters, cluster_id)
    elif z[i, 0] < n and z[i, 1] >= n:
        checked[i] = 1
        clustered[int(z[i, 0])] = 1
        clusters[cluster_id].append(int(z[i, 0]))
        check(z, int(z[i, 1]) - n, n, clustered, checked, clusters, cluster_id)
    else: # z[i, 0] >= n and z[i, 1] >= n
        checked[i] = 1
        check(z, int(z[i, 0]) - n, n, clustered, checked, clusters, cluster_id)
        check(z, int(z[i, 1]) - n, n, clustered, checked, clusters, cluster_id)
    return

def find_mid(x, y, x1, y1, img):

    """Correct the original x, y to the middle of the lane marker, prevent skewed line"""
    # assert img[x, y] == 255, "line tip pixel not on a lane marker!"
    # go along the line until a white pixel is found on it

    length = 0
    dx = x1 - x
    dy = y1 - y
    d = (dx**2 + dy**2)**0.5
    dx = dx / (0.0 + d)
    dy = dy / (0.0 + d) # normalized to unit vector
    x_inc = x
    y_inc = y
    while img[x_inc, y_inc] == 0:
        length += 1
        x_inc = x + int(length * dx);
        y_inc = y + int(length * dy);
    step = 0
    while (img[x_inc, y_inc] != 0) and (step <= 5):
        length += 1
        step += 1
        x_inc = x + int(length * dx);
        y_inc = y + int(length * dy);
    length -= 1
    x_inc = x + int(length * dx);
    y_inc = y + int(length * dy);

    l = y_inc
    r = y_inc
    x_mid = x_inc
    while (img[x_mid, l] == 255) and (l > 0):
        l -= 1
    while (img[x_mid, r] == 255) and (r < img.shape[1] - 1):
        r += 1
    y_mid = (l + r) / 2
    return x_mid, y_mid

def preprocess(filename, line_type, suppress_output):
    # pre-process the image of connected lines, final result masked_img
    img = cv2.imread(filename)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if suppress_output is None:
        cv2.imwrite( "test_gray_image" + line_type + ".png", gray_img)

    ret, thresh_img = cv2.threshold(gray_img, 150, 255, cv2.THRESH_BINARY)
    if suppress_output is None:
        cv2.imwrite('thresh_img.png', thresh_img)

    thresh_img = cv2.resize(thresh_img, (0, 0), fx = downsample_scale, fy = downsample_scale) # image downsample, but will be converted back to gray image again!!!
    ret, thresh_img = cv2.threshold(thresh_img, 20, 255, cv2.THRESH_BINARY)
    img = cv2.resize(img, (0, 0), fx = downsample_scale, fy = downsample_scale) # image downsample

    # mask the original graph
    APPLY_MASK = 0 # 1: apply, 0: not apply
    x_size = thresh_img.shape[1]
    y_size = thresh_img.shape[0]
    mask = np.zeros_like(thresh_img)
    pt1 = (0, 0) # specify 8 vertices of the (U-shaped, concave) mask
    pt2 = (int(0.3 * x_size), 0)
    pt3 = (pt2[0], int(0.57 * y_size)) # default 0.57
    pt4 = (int(0.7 * x_size), pt3[1])
    pt5 = (pt4[0], 0)
    pt6 = (x_size - 1, 0)
    pt7 = (x_size - 1, int(y_size * 0.88))
    pt8 = (0, int(y_size * 0.88))
    vertices = np.array([[pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]])
    mask = cv2.fillPoly(mask, vertices, 255)
    if APPLY_MASK:
        masked_img = cv2.bitwise_and(thresh_img, mask) # apply mask!
    else:
        masked_img = thresh_img # uncomment this if don't wanna use mask!
    if suppress_output is None:
        cv2.imwrite('masked_img_' + line_type + '.png', masked_img)

    return masked_img

def adjust(k, b, y_size, x_size, img, suppress_output):

    # line function: y = kx + b
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
    while ((img[y, x] == 0) or (step < 2)) and all_step < 20:
        length += 1
        x = x0 + int(length * dx)
        y = y0 + int(length * dy)
        if img[y, x] == 255: step += 1
        all_step += 1
    x0 = x
    y0 = y
    l = x
    r = x
    while (img[y, l] == 255) and l > 0: l -= 1
    while (img[y, r] == 255) and r < x_size - 1: r += 1
    x = (l + r) / 2
    line.append((x, y)) # found the first point *on* the lane marking
    length = 0

    # the 0.4, 0.6, 0.4 are define the mask we are applying
    # has to be lower than vanishing point, or the ipm'ed polyline's end point will be negative
    while (x > 0) and (x < x_size - 1) and \
          (y > 0.45 * y_size): # ( (x < int(x_size * 0.3)) or (x > int(x_size * 0.7)) or (y > int(0.45 * y_size)) ):
        length += 10
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
                l = x
                r = x
                while img[y, l] == 255 and l > 0: l -= 1
                while img[y, r] == 255 and r < x_size - 1: r += 1
                if (abs(((l + r) / 2) - x) > (r - l) / 6) and abs(dy) > 0.01: # if the deviation is too large from the center of the lane marker
                # if dy < 0.05, the line is too flat. will not adjust x to middle
                    x = (l + r) / 2
                    line.append((x, y))
                    length = 0
                    dx = (x - x0)
                    dy = (y - y0)
                    dl = math.sqrt(dx ** 2.0 + dy ** 2.0)
                    dx /= dl
                    dy /= dl
                    x0 = x
                    y0 = y
                else:
                    line.append((x, y))
            else:
                l = x
                r = x
                step_l = 0
                while img[y, l] == 0 and l > 0 and step_l < 20:
                    l -= 1
                    step_l += 1
                    if img[y, l] == 255: break
                step_r = 0
                while img[y, r] == 0 and r < x_size - 1 and step_r < 20:
                    r += 1
                    step_r += 1
                    if img[y, r] == 255: break
                if img[y, r] == 0 and img[y, l] == 0: # there is a space here!
                    line.append((x, y))
                else:
                    if step_r < step_l:
                        l = r
                    else:
                        r = l
                    while img[y, l] == 255 and l > 0: l -= 1
                    while img[y, r] == 255 and r < x_size - 1: r += 1
                    x = (l + r) / 2
                    line.append((x, y))
                    length = 0
                    dx = (x - x0)
                    dy = (y - y0)
                    dl = math.sqrt(dx ** 2.0 + dy ** 2.0)
                    dx /= dl
                    dy /= dl
                    x0 = x
                    y0 = y
                    
    return line

def IPM_draw(x, y, img, lines):

    npx = np.array(x, dtype = np.int32) # inb order to pass into c++
    npy = np.array(y, dtype = np.int32)
    import IPM
    step = IPM.points_image2ground(npx, npy) # convert npx, npy to ground coordinates
    print npy
    npx = (npx / step.step_x) + 320 # convert from ground coord to ipm image
    npy = -(npy / step.step_y) + 480
    print npx, npy
    tot = 0 # the use of tot: prevent line between the end tip of two polylines
    for i in range(len(lines)): # lines format: lines = [line1, line2, line3, ...], linei = [(x, y), (x, y), ...]
        for j in range(len(lines[i]) - 1):
            cv2.line(img, (int(npx[tot]), int(npy[tot])), (int(npx[tot+1]), int(npy[tot+1])), (0, 0, 255), 1)
            tot += 1
        tot += 1

    cv2.imwrite("ans.png", img)

def main(filename_connectedline, filename_dashedline, dest, suppress_output = None):

    masked_img_connected = preprocess(filename_connectedline, 'connected', suppress_output)
    masked_img_dashed = preprocess(filename_dashedline, 'dashed', suppress_output)
    # Perform houghlines on connected lines
    rho = 1
    theta = np.pi / 180 / 2 # resolution: 1 degree
    min_line_length = threshold # 40 default
    max_line_gap = 40 # 40 
    lines = cv2.HoughLinesP(masked_img_connected, rho, theta, threshold, np.array([]), min_line_length, max_line_gap) # find the lines

    # adjust all lines' end points to middle!
    if lines is None:
        return [], np.array([[]]), np.array([[]])
    for i in range(lines.shape[0]):
        # print lines[i]
        for y1, x1, y2, x2 in lines[i]:
            x1, y1 = find_mid(x1, y1, x2, y2, masked_img_connected)
            x2, y2 = find_mid(x2, y2, x1, y1, masked_img_connected)
            lines[i] = [[y1, x1, y2, x2]]

    # plot the original hughlinesP result!
    if suppress_output is None:
        img = cv2.imread(filename_dashedline)
        img = cv2.resize(img, (0, 0), fx = downsample_scale, fy = downsample_scale)
        if lines is None: return []
        for i in range(lines.shape[0]):
            for x1,y1,x2,y2 in lines[i]:
                cv2.line(img, (x1,y1), (x2,y2), (0, 255, 0), 1) # paint lines in green
        cv2.imwrite('houghlines_dashed.png', img)

    # filter the results, lines too close will be taken as one line!
    # 1. convert the lines to angle-intercept space - NOTE: intercept is on x-axis on the bottom of the image!
    y0 = int(0.67 * masked_img_connected.shape[0])
    n = lines.shape[0]
    y = np.zeros((n, 2), dtype = float) # stores all lines' data
    for i in range(lines.shape[0]):
        for x1,y1,x2,y2 in lines[i]:
            theta = ( math.atan2(abs(y2 - y1), (x2 - x1) * abs(y2 - y1) / (y2 - y1)) / np.pi * 180.0 )
            intercept = ((x1 - x2) * (y0 - y1) / (y1 - y2)) + x1
            y[i, :] = [theta, intercept] # intercept: x value at y = y0

    # 2. perform clustering
    z = cluster.hierarchy.centroid(y) # finish clustering
    ending = 0
    while z[ending, 2] < cluster_threshold: # cluster distance < 10, continue clustering!
        ending += 1
    ending -= 1 # the last cluster where distance < 10

    # below: figure out which point belongs to which cluster
    clustered = np.zeros((n), dtype = int) # each line, whether clustered
    cluster_id = -1
    clusters = []
    checked = np.zeros((n), dtype = int) # each element in z, whether checked
    for i in range(ending, -1, -1):
        if not checked[i]:
            clusters.append([])
            cluster_id += 1
            check(z, i, n, clustered, checked, clusters, cluster_id) # recursively obtain all members in a cluster

    for i in range(n):
        if not clustered[i]:
            clusters.append([i]) # points not clusterd will be a single cluster

    if suppress_output is None:
        print "cluster representatives:"
    ave_lines = []
    for each_cluster in clusters:
        if suppress_output is None:
            print each_cluster
        sum_intercept = 0
        sum_theta = 0
        tot = len(each_cluster)
        for each_line in each_cluster:
            # print y[each_line, 0], y[each_line, 1]
            sum_theta += y[each_line, 0]
            sum_intercept += y[each_line, 1]
        ave_intercept = sum_intercept / tot
        ave_theta = sum_theta / tot
        if ave_theta == 0:
            ave_theta = 0.001 # to prevent runtime error
        if suppress_output is None:
            print ave_intercept, ave_theta
        y1 = y0
        x1 = ave_intercept
        y2 = masked_img_connected.shape[0] / 2
        x2 = x1 + int((y2 - y1) / math.tan(ave_theta / 180.0 * np.pi))
        y3 = masked_img_connected.shape[0]
        x3 = x1 + int((y3 - y1) / math.tan(ave_theta / 180.0 * np.pi))

        # cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 1) # paint lines in green
        # cv2.line(img, (int(x1), int(y1)), (int(x3), int(y3)), (0, 0, 255), 1)
        k = math.tan(ave_theta / 180.0 * np.pi)
        b = - k * ave_intercept + y0
        ave_lines.append((k, b))

    # further adjust all lines - according to dashed line image
    lines = []
    if suppress_output is None:
        print ave_lines
    for (k, b) in ave_lines:
        line = adjust(k, b, masked_img_connected.shape[0], masked_img_connected.shape[1], masked_img_dashed, suppress_output)
        if suppress_output is None:
            print 'The next line is:', line
        lines.append(line)

    # plot the result on original picture
    img = cv2.imread(filename_dashedline)
    img = cv2.resize(img, (0, 0), fx = downsample_scale, fy = downsample_scale)
    final_lines = []
    draw_lines_x = []
    draw_lines_y = []
    for line in lines: # lines format: lines = [line1, line2, line3, ...], linei = [(x, y), (x, y), ...]
        for i in range(len(line) - 1):
            cv2.line(img, line[i], line[i + 1], (0, 0, 255), 1)
            x1, y1 = line[i]
            x2, y2 = line[i + 1]
            k = (y2 - y1)/(x2 - x1 + 0.0001)
            b = y1 - x1*(y2 - y1)/(x2-x1+0.0001) # y = kx + b
            final_lines.append((k, b)) # collect all lines for evaluation
            draw_lines_x.append(x1) # collect all lines for IPM
            draw_lines_y.append(y1)
            if i == len(line) - 2:
                draw_lines_x.append(x2)
                draw_lines_y.append(y2)

    if suppress_output is None:
        img = cv2.resize(img, (0,0), fx=3.33333, fy=3.33333)
        cv2.imwrite(dest + '/houghlines.png', img)

    # Note: the lines here are on shrinked image! need to magnify by 3.333
    for i, x in enumerate(draw_lines_x):
        draw_lines_x[i] = int(3.3333* x)
    for i, y in enumerate(draw_lines_y):
        draw_lines_y[i] = int(3.3333* y)
    canvas = cv2.imread("gt.png")
    IPM_draw(draw_lines_x, draw_lines_y, canvas, lines)

    return final_lines, masked_img_dashed, img

if __name__ == "__main__":
    main('1.png', '2.png', '.', None)