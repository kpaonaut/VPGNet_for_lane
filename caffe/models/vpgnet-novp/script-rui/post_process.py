import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time # time the execution time

import caffe
import cv2

import shelve

def main():
    workspace_root = 'workspace/4/'
    if not os.path.exists(os.path.join(os.getcwd(), workspace_root)):
        os.mkdir(workspace_root)
    shelf_file_handle = shelve.open(workspace_root + 'shelve.out', 'n')
    # Method1: use a threshold to filter through and directly apply houghlines algorithm


if __name__ == "__main__":
    main()