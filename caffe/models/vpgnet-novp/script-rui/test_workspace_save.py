import numpy as np
import cv2

import shelve # store workspace
workspace_root = 'workspace/0/'
shelf_file_handle = shelve.open(workspace_root + 'shelve.out')

for key in shelf_file_handle.keys():
    print 'restoring variable: ', key
    globals()[key] = shelf_file_handle[key]
shelf_file_handle.close()

