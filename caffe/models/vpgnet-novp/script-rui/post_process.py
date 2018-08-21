import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time # time the execution time

import caffe
import cv2

import shelve

def main():
    workspace_root = './workspace/4/'
    if not os.path.exists(os.path.join(os.getcwd(), workspace_root)):
        os.mkdir(workspace_root)
    shelf_file_handle = shelve.open(workspace_root + 'shelve.out')
    for key in shelf_file_handle:
        globals()[key] = shelf_file_handle[key]
        print key
    shelf_file_handle.close()
    # Method1: use a threshold to filter through and directly apply houghlines algorithm
    resized_mask = cv2.resize(small_mask, (640, 480)) # UNKNOWN bug here: resized_mask cannot be loaded directly from shelve
    ret, thresholded_img = cv2.threshold(resized_mask, 70, 255, cv2.THRESH_BINARY)
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    imgplot = plt.imshow(thresholded_img)
    plt.show()
    cv2.imwrite("thresholded.png", thresholded_img)

if __name__ == "__main__":
    main()