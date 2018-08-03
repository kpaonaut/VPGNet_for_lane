import numpy as np
import matplotlib.pyplot as plt
import sys
import caffe
import cv2

model = '/home/rui/VPGNet/caffe/models/vpgnet-novp/deploy.prototxt'
pretrained = '/home/rui/VPGNet/caffe/models/vpgnet-novp/snapshots/split_iter_100000.caffemodel'

caffe.set_mode_gpu()
caffe.set_device(0)

net = caffe.Net(model, pretrained, caffe.TEST)
img = caffe.io.load_image('../example.png')

transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))  # move image channels to outermost dimension
transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
transformed_img = transformer.preprocess('data', img)

net.blobs['data'].data[...] = [transformed_img]
net.forward()

print net.blobs['binary-mask'].data

vp = net.blobs['binary-mask'].data
print vp.shape
print transformed_img.shape

tot = 0
for i in range(120):
    for j in range(160):
        if vp[0, 0, i, j] > 0.5:
            vp[0, 0, i, j] = 255
            tot += 1
        else:
            vp[0, 0, i, j] = 0
        if vp[0, 1, i, j] > 0.5:
            vp[0, 1, i, j] = 255
            tot += 1
        else:
            vp[0, 1, i, j] = 0
print tot
print vp
cv2.imwrite('mask0.png', vp[0, 0, ...])
cv2.imwrite('mask1.png', vp[0, 1, ...])

classification = net.blobs['multi-label'].data
print classification
classes = []
print classification.shape
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
print classes

bb = net.blobs['bb-output-tiled'].data
print bb.shape