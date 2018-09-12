#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Notice: this program works well for lane output of dashed lines. All parameters are tuned
# for the test data in /lane/lane_test_data/outputForConnectedWideDash
# usage example: python lane_extension_polyline_for_MultiNet.py unity/4.png
import cv2
import numpy as np
import math
import scipy
from scipy import cluster
import IPM
import sys
import time
from adjust import adjust
import adjust_line_for_VPG
import argparse


# define parameters:
DOWNSCALE = 1.0 # 0.3 default
UPSCALE = 1.0 / DOWNSCALE
IMAGE_SIZE_RESCALE = 3 # when the image for ipm is 640 * 480, this var is 1 (defined in camera.conf)
                       # when the image for ipm is 160 * 120, this var is 4
                       # remember to modify all parameters in camera.conf to fit this data!
DEST = "./output_log" # where the output pix are stored, can be changed by arg


def check(z, i, n, clustered, checked, clusters, cluster_id):
    """
    Figures out which member belongs to which cluster after the scipy lib carries out the clustering algorithm
    and stores the process of the clustering in z
    See detailed usage in the example below in cluster_lines(), where this function is called
    """

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


def generate_camera_conf_file(scale):
    """
    Generates camera.conf for IPM.cpp to use as parameters.
    All parameters are scalable to scale. The baseline picture size when scale=1 is 640*480
    However, if in IPM.cpp, parse_config(filename, ipmWidth, ipmHeight, cameraInfo, ipmInfo, UNITY) is used,
    then changing this function will not help change the parameters in IPM.cpp.
    """
    with open('camera.conf', 'w') as f:
        f.write('ipmWidth ' + str(int(640 / scale)) + '\n') # output size!
        f.write('ipmHeight ' + str(int(480 / scale)) + '\n')
        f.write('vpPortion 0.05\n') # how far is the image top from vanishing point (bc vp is too far, can't display all)
        f.write('ipmLeft 0\n') # 85 # pixel range on input to transfer
        f.write('ipmRight ' + str(int(640 / scale) - 1) + '\n')
        f.write('ipmTop ' + str(int(50 / scale)) + '\n')
        f.write('ipmBottom ' + str(int(480 / scale) - 1) + '\n')
        f.write('ipmInterpolation 0\n')
        f.write('focalLengthX %d\n'%(309 / scale)) #
        f.write('focalLengthY %d\n'%(344 / scale)) #
        f.write('opticalCenterX ' + str(int(318 / scale) - 1) + '\n') #
        f.write('opticalCenterY ' + str(int(257 / scale) - 1) + '\n') #
        f.write('cameraHeight 2180\n') # in mm
        f.write('pitch 14.0\n') # in degrees
        f.write('yaw  0.0\n')
        f.write('imageWidth ' + str(int(640 / scale)) + '\n')
        f.write('imageHeight ' + str(int(480 / scale)))


def preprocess(file, line_type, suppress_output): # 0.006s
    '''pre-process the image of connected lines, final result masked_img'''

    # NOTICE! picture has to be float when passed into IPM cpp, return value is also float!
    # the image for adjust() is always 640 * 480
    # file is a gray image!

    generate_camera_conf_file(IMAGE_SIZE_RESCALE) # change camera configuration for IPM according to IMAGE_SIZE_RESCALE
    tmp = file
    # tmp = tmp.astype(dtype = np.float32, copy = False)
    resize_x, resize_y = tmp.shape[1] / 640.0, tmp.shape[0] / 480.0

    ret, tmp = cv2.threshold(tmp, 200, 255, cv2.THRESH_BINARY)
    if not suppress_output:
        cv2.imwrite('%s/%s'%(DEST, 'threshold_original.png'), tmp)

    #tmp = cv2.resize(tmp, (640 / IMAGE_SIZE_RESCALE, 480 / IMAGE_SIZE_RESCALE)) # resize to smaller img for fast ipm
    #tmp = tmp.astype(dtype = np.float32, copy = False)
    # time1 = time.time() # timing
    # ipm_img = np.zeros(tmp.shape[0:2], dtype = np.float32)
    # ipm_gnd_converter = IPM.image_ipm(tmp, ipm_img) # ipm'ed image stored in ipm_img
    # #ipm_img = cv2.GaussianBlur(ipm_img, (10, 10), 0)
    # ipm_img = cv2.blur(ipm_img, (10 / IMAGE_SIZE_RESCALE, 10 / IMAGE_SIZE_RESCALE))
    #time2 = time.time() # timing
    #print "IPM time:", time2 - time1
    #if not suppress_output:
    #    cv2.imwrite('%s/%s'%(DEST, "debug.png"), ipm_img)
 
    # ipm_img = tmp # temporary, FIXME
    # tmp = tmp.astype(dtype = np.uint8, copy = False)
    thresh_img = cv2.resize(tmp, (int(DOWNSCALE * 640), int(DOWNSCALE * 480))) # image downsample, but will be converted back to gray image again!!!
    ret, thresh_img = cv2.threshold(thresh_img, 100, 255, cv2.THRESH_BINARY)
    thresh_img = thresh_img.astype(np.uint8)
    
    #time3 = time.time()
    #print time1 - time0, time2 - time1, time3 - time2
    # mask the original graph
    APPLY_MASK = 0 # 1: apply, 0: not apply
    x_size = thresh_img.shape[1]
    y_size = thresh_img.shape[0]
    
    # below: a mask of shape 凹
    # pt1 = (0, 0) # specify 8 vertices of the (U-shaped, concave) mask
    # pt2 = (int(0.01 * x_size), 0)
    # pt3 = (pt2[0], int(0.1 * y_size)) # default 0.57
    # pt4 = (int(0.99 * x_size), pt3[1])
    # pt5 = (pt4[0], 0)
    # pt6 = (x_size - 1, 0)
    # pt7 = (x_size - 1, int(y_size * 1))
    # pt8 = (0, int(y_size * 1))

    # below: a mask of shape 凸
    if APPLY_MASK:
        pt1 = (0, int(0.2 * y_size)) # specify 8 vertices of the (U-shaped, concave) mask
        pt2 = (int(0.45 * x_size), int(0.2 * y_size))
        pt3 = (pt2[0], int(0.01 * y_size)) # default 0.57
        pt4 = (int(0.55 * x_size), pt3[1])
        pt5 = (pt4[0], int(0.2 * y_size))
        pt6 = (x_size - 1, int(0.2 * y_size))
        pt7 = (x_size - 1, int(y_size * 1))
        pt8 = (0, y_size - 1)

        mask = np.zeros_like(thresh_img)
        vertices = np.array([[pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]])
        mask = cv2.fillPoly(mask, vertices, 255)
        masked_img = cv2.bitwise_and(thresh_img, mask) # apply mask!
    else:
        masked_img = thresh_img # don't wanna use mask!
    if not suppress_output:
        cv2.imwrite('%s/%s'%(DEST, 'thresh_img.png'), thresh_img)
        cv2.imwrite('%s/%s'%(DEST, 'masked_img.png'), masked_img)

    return masked_img, resize_x, resize_y


def houghlines(masked_img_connected, suppress_output):
    """Performs houghlines algorithm"""
    scale = 0.5 # 0.175 # scale the pic to perform houghlinesP, for speed!
    rho = 2
    theta = np.pi / 180 # / 2 # resolution: 0.5 degree
    threshold = int(150 * scale * DOWNSCALE) # the number of votes (voted by random points on the picture)
    min_line_length = int(80 * scale * DOWNSCALE) # line length
    max_line_gap = 20 * scale # the gap between points on the line, no limit here
    masked_img_connected = cv2.resize(masked_img_connected, (0, 0), fx = scale, fy = scale)
    lines = cv2.HoughLinesP(masked_img_connected, rho, theta, threshold, np.array([]), min_line_length, max_line_gap) # find the lines

    # adjust all lines' end points to middle!
    if lines is None:
        return None
    for i in range(lines.shape[0]):
        for y1, x1, y2, x2 in lines[i]:
            #x1, y1 = find_mid(x1, y1, x2, y2, masked_img_connected)
            #x2, y2 = find_mid(x2, y2, x1, y1, masked_img_connected)
            lines[i] = [[int(y1 / scale), int(x1 / scale), int(y2 / scale), int(x2 / scale)]]

    # plot the original hughlinesP result!
    if not suppress_output:
        hough_img = masked_img_connected.copy()
        cv2.imwrite('%s/%s'%(DEST, 'houghlines_raw.png'), hough_img)
        hough_img = cv2.imread('%s/%s'%(DEST, 'houghlines_raw.png')) # convert gray scale to BGR
        if lines is None: return []
        for i in range(lines.shape[0]):
            for x1,y1,x2,y2 in lines[i]:
                cv2.line(hough_img, (int(x1*scale), int(y1*scale)), (int(x2*scale), int(y2*scale)), (0, 255, 0), 1) # paint lines in green

        # hough_img = cv2.resize(hough_img, (0, 0), fx = UPSCALE, fy = UPSCALE)
        cv2.imwrite('%s/%s'%(DEST, 'houghlines_raw.png'), hough_img)
    return lines # lines in 640 * 480 * DOWNSCALE pic


def cluster_lines(masked_img_connected, lines, suppress_output):
    """
    Clusters the results from houghlines(), lines too close will be clustered into one line.
    "centroid", distances from cluster is determined by the distance of centroids.
    """
    # filter the results, lines too close will be taken as one line!
    # 1. convert the lines to angle-intercept space - NOTE: intercept is on x-axis on the bottom of the image!
    cluster_threshold = int(40 * DOWNSCALE)
    y0 = int(0.7 * masked_img_connected.shape[0])
    n = lines.shape[0]

    if n == 0: # n = 0 or 1, can't do cluster!
        return []
    if n == 1:
        print lines[0]
        [[x1, y1, x2, y2]] = lines[0]
        eps = 0.1
        theta = ( math.atan2(abs(y2 - y1), (x2 - x1) * abs(y2 - y1) / (y2 - y1 + eps)) / np.pi * 180.0)
        intercept = ((x1 - x2) * (y0 - y1) / (y1 - y2 + eps)) + x1
        k = math.tan(theta / 180.0 * np.pi)
        b = - k * intercept + y0
        return [(k, b)]

    y = np.zeros((n, 2), dtype = float) # stores all lines' data
    for i in range(lines.shape[0]):
        for x1,y1,x2,y2 in lines[i]:
            eps = 0.1 # prevent division by 0
            theta = ( math.atan2(abs(y2 - y1), (x2 - x1) * abs(y2 - y1) / (y2 - y1 + eps)) / np.pi * 180.0)
            intercept = ((x1 - x2) * (y0 - y1) / (y1 - y2 + eps)) + x1
            y[i, :] = [theta * DOWNSCALE, intercept] # intercept: x value at y = y0

    # 2. perform clustering
    z = cluster.hierarchy.centroid(y) # finish clustering
    ending = 0
    while ending < z.shape[0] and z[ending, 2] < cluster_threshold: # cluster distance < cluster_threshold, continue clustering!
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

    if not suppress_output:
        print "cluster representatives: format (intercept, theta)"

    ave_lines = []
    for each_cluster in clusters:
        if not suppress_output:
            print each_cluster
        sum_intercept = 0
        sum_theta = 0
        tot = len(each_cluster)
        for each_line in each_cluster:
            sum_theta += y[each_line, 0] / DOWNSCALE
            sum_intercept += y[each_line, 1]
        ave_intercept = sum_intercept / tot
        ave_theta = sum_theta / tot
        if ave_theta == 0:
            ave_theta = 0.001 # to prevent runtime error
        if not suppress_output:
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

    if not suppress_output:
        print "cluster representatives all printed!"

    return ave_lines


def cluster_directions(ave_lines, suppress_output):
    """
    Further cluster the lines according to their inclination only.

    Based on the assumption that most lane markings are parallel,
    we filter the noise by thresholding. The lane markings whose
    inclination is too different from others will be picked out by
    the clustering algorithm("single", distance is determined by the closest point) 
    and taken as noises.
    """
    n = len(ave_lines)
    y = np.zeros((n, 1), dtype = float)
    for i, (k, b) in enumerate(ave_lines):
        y[i] = math.atan2(abs(k), abs(k)/k) / np.pi * 180
    z = cluster.hierarchy.linkage(y, method='single', metric='euclidean')

    ending = 0
    cluster_threshold = 15 # override the globally defined cluster_threshold for houghlines clustering
    while ending < z.shape[0]\
        and z[ending, 2] < cluster_threshold: # cluster distance < 10, continue clustering!
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

    if not suppress_output:
        print z
        print clusters
    # print max_cluster_id

    filtered_lines = []
    for line_id in clusters[max_cluster_id]:
        filtered_lines.append(ave_lines[line_id])

    # print filtered_lines
    return filtered_lines

def make_sparse(lines):
    """
    Makes polyline sparse by a scale
    """
    sparse_scale = 8
    sparse_lines = []
    npx = np.array([])
    npy = np.array([])
    for line in lines:
        tmp = []
        for i in range(len(line)):
            if line[i, 1] != 0 or line[i, 0] != 0:
                last = i
            if line[i, 1] == 0 and line[i, 0] == 0: # get rid of the additional 0s in line[]
                break
            if i % sparse_scale == 0:
                tmp.append(line[i])
                npx = np.append(npx, line[i, 0])
                npy = np.append(npy, line[i, 1])
        if tmp == []:
            continue
        if len(tmp) == 1: # only one point in line, invalid! add the last point also
            tmp.append(line[last])
            npx = np.append(npx, line[last, 0])
            npy = np.append(npy, line[last, 1])
        sparse_lines.append(tmp)
    npx = npx.astype(dtype=np.float32, copy=False)
    npy = npy.astype(dtype=np.float32, copy=False)
    return npx, npy, sparse_lines


def clean_up(orig_img, lines, suppress_output): # orig_image: 640 * 480
    # plot the result on original picture
    threshold_img = cv2.imread('%s/%s'%(DEST, "thresh_img.png"))

    # final_lines = []
    draw_lines_x = []
    draw_lines_y = []

    # make polyline sparser
    npx, npy, lines = make_sparse(lines)

    # print polyline
    for line in lines:
        print 'The next line is:', line

    for line in lines: # lines format: lines = [line1, line2, line3, ...], linei = np.array([[x, y], [x, y], ...])
        for i in range(len(line) - 1):
            if not suppress_output:
                cv2.line(threshold_img, (int(line[i][0]), int(line[i][1])), (int(line[i + 1][0]), int(line[i + 1][1])), (0, 0, 255), 1)
            x1, y1 = line[i]
            x2, y2 = line[i + 1]
            # k = (y2 - y1)/(x2 - x1 + 0.0001)
            # b = y1 - x1*(y2 - y1)/(x2-x1+0.0001) # y = kx + b
            # final_lines.append((k, b)) # collect all lines for evaluation
            draw_lines_x.append(x1 * UPSCALE / IMAGE_SIZE_RESCALE) # collect all lines for IPM
            draw_lines_y.append(y1 * UPSCALE / IMAGE_SIZE_RESCALE)
            if i == len(line) - 2:
                draw_lines_x.append(x2 * UPSCALE / IMAGE_SIZE_RESCALE)
                draw_lines_y.append(y2 * UPSCALE / IMAGE_SIZE_RESCALE)

    # lines[] here is within image of 640 * 480
    npx = np.array(draw_lines_x, dtype = np.float32) # in order to pass into c++
    npy = np.array(draw_lines_y, dtype = np.float32)

    #step = IPM.points_ipm2image(npx, npy) # convert npx, npy to picture coordinates

    tot = 0
    for line in lines: # lines format: lines = [line1, line2, line3, ...], linei = [(x, y), (x, y), ...]
        for i in range(len(line) - 1):
            cv2.line(orig_img, (int(npx[tot]*IMAGE_SIZE_RESCALE), int(npy[tot]*IMAGE_SIZE_RESCALE)), \
                (int(npx[tot+1]*IMAGE_SIZE_RESCALE), int(npy[tot+1]*IMAGE_SIZE_RESCALE)), (0, 0, 255), 1)
            tot += 1
        tot += 1

    cv2.imwrite('%s/%s'%(DEST, 'threshold.png'), threshold_img)
    cv2.imwrite('%s/%s'%(DEST, "labeled.png"), orig_img)

    return lines, npx, npy


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


def convert_ipm2gnd(ipm_gnd_converter, lines):

    # the coordinates need to be rescaled into an image of (640 * 480) * IMAGE_SIZE_RESCALE, which is the ipm coordinates,
    # then, the coordinates can be transformed to ground coordinates
    for line in lines:
        for i in range(len(line)):
            line[i][0] = (line[i][0] / DOWNSCALE / IMAGE_SIZE_RESCALE - ipm_gnd_converter.ipmWidth / 2) * ipm_gnd_converter.step_x + (ipm_gnd_converter.xfMax + ipm_gnd_converter.xfMin) / 2.0
            line[i][1] = (ipm_gnd_converter.ipmHeight - line[i][1] / DOWNSCALE / IMAGE_SIZE_RESCALE) * ipm_gnd_converter.step_y + ipm_gnd_converter.yfMin
    return lines


def work(file, do_adjust, suppress_output, time1, time2): # the public API
    # threshold + resize
    masked_img_connected, resize_x, resize_y = preprocess(file, 'connected', suppress_output) # img: ipm'ed image
    # masked_img_connected: (640 * 480)*DOWNSCALE
    if not suppress_output:
        orig_img = cv2.resize(file, (640, 480))
        cv2.imwrite('%s/%s'%(DEST, "o.png"), orig_img)
        orig_img = cv2.imread('%s/%s'%(DEST, "o.png"))

    # initial line extraction: with opencv HoughLines algorithm
    time25 = time.time()
    lines = houghlines(masked_img_connected, suppress_output) # (640 * 480)*DOWNSCALE
    time3 = time.time()

    if lines is not None:

        ave_lines = cluster_lines(masked_img_connected, lines, suppress_output) # cluster results from houghlines
        # further cluster and filter out the lines that are noises! only retain the largest cluster whose inclinations are close enough
        # ave_lines = cluster_directions(ave_lines, suppress_output)
        time4 = time.time()

        lines = []

        for (k, b) in ave_lines:
            if not suppress_output:
                # print k, b

            if do_adjust:
                # do adjustment (refinement), further adjust all lines to the middle
                # line = adjust(k, b, masked_img_connected.shape[0], masked_img_connected.shape[1], masked_img_connected, DOWNSCALE) # python adjust
                line = np.zeros((200, 2), dtype = np.int32) # C++ adjust
                masked_img_connected = np.array(masked_img_connected, dtype = np.int32)
                adjust_line_for_VPG.adjust(line, k, b, DOWNSCALE, masked_img_connected) # C++ adjust

            else:
                # only use straight line, don't do refinement
                y = masked_img_connected.shape[0] - 1
                line = np.array([[int((y - b)/k), y]])
                while y >= 10 * DOWNSCALE:
                    y -= int(10 * DOWNSCALE)
                    line = np.append(line, [[int((y - b)/k), y]], axis = 0) # lines are in the image of the size (640 * 480)*DOWNSCALE

            if line != [] and (line[0, 0] != 0 or line[0, 1] != 0): # this line exists
                lines.append(line)

        time5 = time.time() # lines are in the image of the size (640 * 480)* DOWNSCALE
        if lines != []:

            # filter through lines, make polyline control points sparser, and convert them to image coordinates
            if not suppress_output:
                lines, npx, npy = clean_up(orig_img, lines, suppress_output)
                # rescale npx, npy back to original image (not 640*480!) and store in the same shape as lines
                lines_in_img = scale_back(lines, npx, npy, resize_x, resize_y)
                # further convert to ground coordinates: (real-world)
                lines_in_gnd = convert_img2gnd(npx, npy, lines)
                print lines_in_gnd

            else:
                npx, npy, lines = make_sparse(lines) # lines are in image of (640 * 480) * DOWNSCALE; real ipm is in (640 * 480) / IMAGE_SIZE_RESCALE
                lines_in_gnd = convert_img2gnd(npx, npy, lines) # Note: this function also modifies lines[]!
                # lines format: a list of numpy ndarrays [line1, line2, ...], line1 = np.array( [[x1, y1], [x2, y2], ...] )
        else:
            lines_in_gnd = []
    
    else:
        lines_in_gnd = []
        lines = []

    time6 = time.time()
    #print "readfile time: ", time2 - time1, "preprocess:", time25 - time2, "houghlines: ", time3 - time25, "clustering: ", time4 - time3
    #print "adjust in C++: ", time5 - time4, "clean up: ", time6 - time5, "total time: ", time6 - time1
    #print "total time not counting file reading: ", time6 - time2

    return time6 - time2, lines_in_gnd, lines


def main(filename, do_adjust, suppress_output=None):

    # For the sake of speed and performance, we rescale the image several times.
    # The input image is not necessarily 640 * 480, but we can use 640 * 480 as the datum for resizing.
    # We also resize the original pic to 640 * 480 for visualized output for debug.
    # Second, resize by *DOWNSCALE(can be > 1 or < 1) to (640 * 480)*DOWNSCALE, to perform line adjustment
    time1 = time.time()
    file = cv2.imread(filename)
    file = cv2.cvtColor(file, cv2.COLOR_BGR2GRAY) # convert to gray
    time2 = time.time()

    # public API: input grayScale image
    return work(file, do_adjust, suppress_output, time1, time2)


if __name__ == "__main__":
    # Usage:
    # python lane_extension_polyline_for_VPG.py filename
    # python lane_extension_polyline_for_VPG.py filename -a
    # python lane_extension_polyline_for_VPG.py filename -a -o
    # python lane_extension_polyline_for_VPG.py filename -a -o -d <directory>

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="specify the path to the input picture")
    parser.add_argument("-a", "--adjust", help="adjust along the line to get a polyline instead of the original straight line", action = "store_true")
    parser.add_argument("-o", "--output", help="output the pictures, otherwise there is no output", action = "store_true")
    parser.add_argument("-d", "--directory", type=str, help="the directory where output pix are stored")
    args = parser.parse_args()
    if args.directory:
        DEST = args.directory
    main(args.filename, do_adjust=args.adjust, suppress_output=not args.output)