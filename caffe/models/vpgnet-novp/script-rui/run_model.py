import numpy as np
import matplotlib.pyplot as plt
import sys
import time # time the execution time

import caffe
import cv2

model = '/home/rui/VPGNet/caffe/models/vpgnet-novp/deploy_Rui.prototxt' # deploy_Rui: pruned useless branches
pretrained = '/home/rui/VPGNet/caffe/models/vpgnet-novp/snapshots/split_iter_100000.caffemodel'

caffe.set_mode_gpu()
caffe.set_device(0)

net = caffe.Net(model, pretrained, caffe.TEST)
# visualize net shape:
# for name, blob in net.blobs.iteritems():
#    print("{:<5}: {}".format(name, blob.data.shape))

img = caffe.io.load_image('../example.png')

print "Start timing!"
t = time.time()

transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost dimension
transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
transformed_img = transformer.preprocess('data', img)
# print transformed_img
# swap R, B channel, the final input to the network should be RGB
tmp = np.copy(transformed_img[0])
transformed_img[0] = transformed_img[2]
transformed_img[2] = tmp

net.blobs['data'].data[...] = transformed_img
t1 = time.time()
for i in range(100):
    net.forward()
    # for j in range(1000000): # mimic post process
    #     pass
print "forward propagation time: ", time.time() - t1

dt = time.time() - t
print "Timing ends! Process time:", dt

img = cv2.imread('../example.png')
for i in range(3):
    for j in range(transformed_img.shape[1]):
        for k in range(transformed_img.shape[2]):
            img[j, k, i] = transformed_img[i, j, k]
cv2.imwrite("example_imported.png", img)

# obj_mask = net.blobs['binary-mask'].data
# print obj_mask.shape
# print transformed_img.shape

# masked_img = img.copy()
# mask_grid_size = img.shape[0] / obj_mask.shape[2]
# tot = 0
# for i in range(120):
#     for j in range(160):
#         if obj_mask[0, 0, i, j] > 0.5:
#             obj_mask[0, 0, i, j] = 255
#             tot += 1
#         else:
#             obj_mask[0, 0, i, j] = 0
#             masked_img[i*mask_grid_size : (i+1)*mask_grid_size + 1, j*mask_grid_size : (j+1)*mask_grid_size + 1] = (255, 255, 255) # mask with white block
#         if obj_mask[0, 1, i, j] > 0.5:
#             obj_mask[0, 1, i, j] = 255
#             tot += 1
#         else:
#             obj_mask[0, 1, i, j] = 0
# cv2.imwrite('mask0.png', obj_mask[0, 0, ...])
# cv2.imwrite('mask1.png', obj_mask[0, 1, ...])
# cv2.imwrite('masked.png', masked_img)

classification = net.blobs['multi-label'].data
classes = []


# create color for visualizing classification
def color_options(x):
    return {
        1: (0, 255, 0), # green color
        2: (255, 0, 0), # blue
        3: (0, 0, 255), # red
        4: (0, 0, 0)
    }[x]

# visualize classification
grid_size = img.shape[0]/60
for i in range(60):
    classes.append([])
    for j in range(80):
        max_value = 0
        maxi = 0
        for k in range(64):
            if classification[0, k, i, j] > max_value:
                max_value = classification[0, k, i, j]
                maxi = k
        classes[i].append(maxi)
        if maxi != 0:
            pt1 = (j*grid_size, i*grid_size)
            pt2 = (j*grid_size+grid_size, i*grid_size+grid_size)
            # print maxi
            cv2.rectangle(img, pt1, pt2, color_options(maxi), 2)

cv2.imwrite("example_classified.png", img) # ISSUE1: the image BGR channel VS RGB

# bounding box visualization
# bb = net.blobs['bb-output-tiled'].data
# print bb.shape
# bb_visualize0 = bb[0, 0, ...]*255
# bb_visualize1 = bb[0, 1, ...]*255
# bb_visualize2 = bb[0, 2, ...]*255
# bb_visualize3 = bb[0, 3, ...]*255
# cv2.imwrite('bb_visualize0.png', bb_visualize0)
# cv2.imwrite('bb_visualize1.png', bb_visualize1)
# cv2.imwrite('bb_visualize2.png', bb_visualize2)
# cv2.imwrite('bb_visualize3.png', bb_visualize3)