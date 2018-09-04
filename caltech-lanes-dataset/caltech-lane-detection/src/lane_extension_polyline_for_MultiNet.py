# Notice: this program works well for lane output of continuous lines. All parameters are tuned
# for the test data in /lane/lane_test_data/outputForConnectedWideDash
# usage example: python lane_extension_polyline_for_MultiNet.py unity/4.png
import cv2
import numpy as np
import math
import scipy
from scipy import cluster
import IPM
import sys

# define parameters:
downscale = 4.0 # 0.3 default
upscale = 1.0 / downscale
cluster_threshold = int(2.5 * 3.33 / upscale)
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
    '''pre-process the image of connected lines, final result masked_img'''

    # NOTICE! picture has to be float when passed into IPM cpp, return value is also float!
    tmp = cv2.imread(filename)
    tmp = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
    resize_x, resize_y = tmp.shape[1] / 640.0, tmp.shape[0] / 480.0
    tmp = cv2.resize(tmp, (640, 480))
    original_img = tmp.copy()
    tmp = tmp.astype(dtype = np.float32, copy = False)
    img = np.zeros(tmp.shape[0:2], dtype = np.float32)
    IPM.image_ipm(tmp, img)
    img = img.astype(dtype = np.uint8, copy = False)

    if suppress_output is None:
        pass # cv2.imwrite( "test_gray_image" + line_type + ".png", img)

    ret, thresh_img = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)
    if suppress_output is None:
        cv2.imwrite('thresh_img.png', thresh_img)

    thresh_img = cv2.resize(thresh_img, (0, 0), fx = downscale, fy = downscale) # image downsample, but will be converted back to gray image again!!!
    ret, thresh_img = cv2.threshold(thresh_img, 20, 255, cv2.THRESH_BINARY)
    img = cv2.resize(img, (0, 0), fx = downscale, fy = downscale) # image downsample

    # mask the original graph
    APPLY_MASK = 1 # 1: apply, 0: not apply
    x_size = thresh_img.shape[1]
    y_size = thresh_img.shape[0]
    mask = np.zeros_like(thresh_img)
    
    # pt1 = (0, 0) # specify 8 vertices of the (U-shaped, concave) mask
    # pt2 = (int(0.01 * x_size), 0)
    # pt3 = (pt2[0], int(0.1 * y_size)) # default 0.57
    # pt4 = (int(0.99 * x_size), pt3[1])
    # pt5 = (pt4[0], 0)
    # pt6 = (x_size - 1, 0)
    # pt7 = (x_size - 1, int(y_size * 1))
    # pt8 = (0, int(y_size * 1))

    pt1 = (0, int(0.1 * y_size)) # specify 8 vertices of the (U-shaped, concave) mask
    pt2 = (int(0.4 * x_size), int(0.1 * y_size))
    pt3 = (pt2[0], int(0.01 * y_size)) # default 0.57
    pt4 = (int(0.6 * x_size), pt3[1])
    pt5 = (pt4[0], int(0.1 * y_size))
    pt6 = (x_size - 1, int(0.1 * y_size))
    pt7 = (x_size - 1, int(y_size * 1))
    pt8 = (0, y_size - 1)

    vertices = np.array([[pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]])
    mask = cv2.fillPoly(mask, vertices, 255)
    if APPLY_MASK:
        masked_img = cv2.bitwise_and(thresh_img, mask) # apply mask!
    else:
        masked_img = thresh_img # uncomment this if don't wanna use mask!
    if suppress_output is None:
        pass # cv2.imwrite('masked_img_' + line_type + '.png', masked_img)

    return img, masked_img, original_img, resize_x, resize_y

def adjust(k, b, y_size, x_size, img, suppress_output):
    """
    With a good initial guess, adjust the extracted lane lines along the way to the middle of the lane-marking
    """

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
    while ((img[y, x] == 0) or (step < 2)) and all_step < 10 * downscale:
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
          (y > 0.05 * y_size): # ( (x < int(x_size * 0.3)) or (x > int(x_size * 0.7)) or (y > int(0.45 * y_size)) ):
        length += 20
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
                    pass # line.append((x, y))
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

def houghlines(masked_img_connected, img, suppress_output):
    # Perform houghlines on connected lines
    rho = 1
    theta = np.pi / 180 / 2 # resolution: 0.5 degree
    threshold = int(60 * downscale) # the number of votes (voted by random points on the picture)
    min_line_length = int(100 * downscale) # line length
    max_line_gap = 10000 # the gap between points on the line 
    lines = cv2.HoughLinesP(masked_img_connected, rho, theta, threshold, np.array([]), min_line_length, max_line_gap) # find the lines

    # adjust all lines' end points to middle!
    if lines is None:
        return None
    for i in range(lines.shape[0]):
        for y1, x1, y2, x2 in lines[i]:
            x1, y1 = find_mid(x1, y1, x2, y2, masked_img_connected)
            x2, y2 = find_mid(x2, y2, x1, y1, masked_img_connected)
            lines[i] = [[y1, x1, y2, x2]]

    # plot the original hughlinesP result!
    if suppress_output is None:
        hough_img = masked_img_connected.copy()
        cv2.imwrite('houghlines_raw.png', hough_img)
        hough_img = cv2.imread('houghlines_raw.png') # convert gray scale to BGR
        if lines is None: return []
        for i in range(lines.shape[0]):
            for x1,y1,x2,y2 in lines[i]:
                cv2.line(hough_img, (x1,y1), (x2,y2), (0, 255, 0), 1) # paint lines in green
                # print ((x1,y1), (x2,y2))
        hough_img = cv2.resize(hough_img, (0, 0), fx = upscale, fy = upscale)
        print hough_img.shape
        cv2.imwrite('houghlines_raw.png', hough_img)

    return lines

def cluster_lines(masked_img_connected, lines, suppress_output):
    # filter the results, lines too close will be taken as one line!
    # 1. convert the lines to angle-intercept space - NOTE: intercept is on x-axis on the bottom of the image!
    y0 = int(0.6 * masked_img_connected.shape[0])
    n = lines.shape[0]
    y = np.zeros((n, 2), dtype = float) # stores all lines' data
    for i in range(lines.shape[0]):
        for x1,y1,x2,y2 in lines[i]:
            theta = ( math.atan2(abs(y2 - y1), (x2 - x1) * abs(y2 - y1) / (y2 - y1)) / np.pi * 180.0)
            intercept = ((x1 - x2) * (y0 - y1) / (y1 - y2)) + x1
            y[i, :] = [theta * downscale, intercept] # intercept: x value at y = y0

    # 2. perform clustering
    z = cluster.hierarchy.centroid(y) # finish clustering
    ending = 0
    while ending < z.shape[0] and z[ending, 2] < cluster_threshold: # cluster distance < 10, continue clustering!
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
        print "cluster representatives: format (intercept, theta)"

    ave_lines = []
    for each_cluster in clusters:
        if suppress_output is None:
            print each_cluster
        sum_intercept = 0
        sum_theta = 0
        tot = len(each_cluster)
        for each_line in each_cluster:
            sum_theta += y[each_line, 0] / downscale
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

    if suppress_output is None:
        print "cluster representatives all printed!"

    return ave_lines

def cluster_directions(ave_lines):
    n = len(ave_lines)
    y = np.zeros((n, 1), dtype = float)
    for i, (k, b) in enumerate(ave_lines):
        y[i] = math.atan2(abs(k), abs(k)/k) / np.pi * 180
    z = cluster.hierarchy.linkage(y, method='single', metric='euclidean')

    ending = 0
    cluster_threshold = 5 # override the globally defined cluster_threshold for houghlines clustering
    while ending < z.shape[0] and z[ending, 2] < cluster_threshold: # cluster distance < 10, continue clustering!
        ending += 1
    ending -= 1 # the last cluster where distance < 10

    # below: figure out which direction belongs to which cluster
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
            clusters.append([i]) # directions not clusterd will be a single cluster

    max_cluster_size = 0
    max_cluster_id = 0
    for i, clustered_lines in enumerate(clusters):
        l = len(clustered_lines)
        if l > max_cluster_size:
            max_cluster_size = l
            max_cluster_id = i

    print z
    print clusters
    # print max_cluster_id

    filtered_lines = []
    for line_id in clusters[max_cluster_id]:
        filtered_lines.append(ave_lines[line_id])

    # print filtered_lines
    return filtered_lines

def clean_up(img, orig_img, lines, suppress_output):
    # plot the result on original picture
    if suppress_output is None:
        threshold_img = cv2.imread("thresh_img.png")
        img = cv2.resize(img, (0, 0), fx = downscale, fy = downscale)

    final_lines = []
    draw_lines_x = []
    draw_lines_y = []

    # make polyline sparser
    sparse_lines = []
    for line in lines:
        tmp = []
        counter = 0
        for i in range(len(line)):
            if counter % 8 == 0:
                tmp.append(line[i])
            counter += 1
        if len(tmp) == 1: # only one point in line, invalid! add the last point also
            tmp.append(line[len(line) - 1])
        sparse_lines.append(tmp)
    lines = sparse_lines

    # print polyline
    if suppress_output is None:
        for line in lines:
            print 'The next line is:', line

    for line in lines: # lines format: lines = [line1, line2, line3, ...], linei = [(x, y), (x, y), ...]
        for i in range(len(line) - 1):
            if suppress_output is None:
                cv2.line(img, line[i], line[i + 1], (0, 0, 255), 1)
                cv2.line(threshold_img, (int(upscale * line[i][0]), int(upscale * line[i][1])), (int(upscale * line[i + 1][0]), int(upscale * line[i + 1][1])), (0, 0, 255), 1)
            x1, y1 = line[i]
            x2, y2 = line[i + 1]
            k = (y2 - y1)/(x2 - x1 + 0.0001)
            b = y1 - x1*(y2 - y1)/(x2-x1+0.0001) # y = kx + b
            final_lines.append((k, b)) # collect all lines for evaluation
            draw_lines_x.append(x1 * upscale) # collect all lines for IPM
            draw_lines_y.append(y1 * upscale)
            if i == len(line) - 2:
                draw_lines_x.append(x2 * upscale)
                draw_lines_y.append(y2 * upscale)

    npx = np.array(draw_lines_x, dtype = np.float32) # in order to pass into c++
    npy = np.array(draw_lines_y, dtype = np.float32)

    step = IPM.points_ipm2image(npx, npy) # convert npx, npy to picture coordinates

    if suppress_output is None:
        tot = 0
        for line in lines: # lines format: lines = [line1, line2, line3, ...], linei = [(x, y), (x, y), ...]
            for i in range(len(line) - 1):
                cv2.line(orig_img, (int(npx[tot]), int(npy[tot])), (int(npx[tot+1]), int(npy[tot+1])), (0, 0, 255), 1)
                tot += 1
            tot += 1

        img = cv2.resize(img, (0,0), fx=upscale, fy=upscale)
        cv2.imwrite('threshold.png', threshold_img)
        cv2.imwrite("labeled.png", orig_img)

    return final_lines, lines, npx, npy

def scale_back(lines, npx, npy, resize_x, resize_y):
    tot = 0
    lines_in_img = []
    for i in range(len(lines)): # lines format: lines = [line1, line2, line3, ...], linei = [(x, y), (x, y), ...]
        lines_in_img.append([])
        for j in range(len(lines[i])):
            if (npx[tot] >= 0) and (npx[tot] < 640) and (npy[tot] >= 0) and (npy[tot] < 480):
                lines_in_img[i].append((int(npx[tot] * resize_x), int(npy[tot] * resize_y)))
            tot += 1
    return lines_in_img

def convert_img2gnd(npx, npy, lines):
    IPM.points_image2ground(npx, npy)
    tot = 0
    lines_in_gnd = []
    for i in range(len(lines)): # lines format: lines = [line1, line2, line3, ...], linei = [(x, y), (x, y), ...]
        lines_in_gnd.append([])
        for j in range(len(lines[i])):
            if (npy[tot] >= 0):
                lines_in_gnd[i].append((npx[tot], npy[tot]))
            tot += 1
    return lines_in_gnd

def main(filename, dest, do_adjust, suppress_output = None):

    # threshold + resize
    img, masked_img_connected, orig_img, resize_x, resize_y = preprocess(filename, 'connected', suppress_output) # img: ipm'ed image
    if suppress_output is None:
        cv2.imwrite("o.png", orig_img)
        orig_img = cv2.imread("o.png")

    # initial line extraction: with opencv HoughLines algorithm
    lines = houghlines(masked_img_connected, img, suppress_output)

    if lines is not None:

        ave_lines = cluster_lines(masked_img_connected, lines, suppress_output) # cluster results from houghlines

        # further adjust all lines to the middle
        if not do_adjust:
            # need to further cluster and filter out the lines that are noises! only retain the largest cluster this time!
            ave_lines = cluster_directions(ave_lines)

        lines = []

        for (k, b) in ave_lines:
            if suppress_output is None:
                print k, b

            if do_adjust:
                # do adjustment (refinement)
                line = adjust(k, b, masked_img_connected.shape[0], masked_img_connected.shape[1], masked_img_connected, suppress_output)
            else:
                # only use straight line, don't do refinement
                line = []
                y = masked_img_connected.shape[0] - 1
                while y >= 40:
                    line.append((int((y - b)/k), y))
                    y -= 40

            lines.append(line)

        if lines != []:

            # filter through lines, make polyline control points sparser, and convert them to image coordinates
            final_lines, lines, npx, npy = clean_up(img, orig_img, lines, suppress_output)

            # rescale npx, npy back to original image (not 640*480!) and store in the same shape as lines
            lines_in_img = scale_back(lines, npx, npy, resize_x, resize_y)

            # further convert to ground coordinates: (real-world)
            lines_in_gnd = convert_img2gnd(npx, npy, lines)
            
            if suppress_output is None:
                print lines_in_gnd
        
        else:
            lines_in_gnd = []

    
    else:
        lines_in_gnd = []

    return lines_in_gnd

if __name__ == "__main__":
    main(sys.argv[1], '.', do_adjust = False, suppress_output = None)