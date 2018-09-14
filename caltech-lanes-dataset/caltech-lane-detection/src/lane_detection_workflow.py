import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time # time the execution time

import caffe
import cv2

import lane_extension_polyline_for_VPG as pp


class LaneDetector:
    """
    The class which includes the entire pipeline of lane detection
    """

    def __init__(self, workspace_root='.'):
        if not os.path.exists(os.path.join(os.getcwd(), workspace_root)):
            os.mkdir(workspace_root)

        self.model = '/home/rui/VPGNet/caffe/models/vpgnet-novp/deploy_only_binary.prototxt' # pruned model, only outputs binary mask
        self.pretrained = '/home/rui/VPGNet/caffe/models/vpgnet-novp/snapshots/split_iter_50000.caffemodel'
        caffe.set_mode_gpu()
        caffe.set_device(0)
        self.net = caffe.Net(self.model, self.pretrained, caffe.TEST)

    def load_image(self, filename):
        """ load image from filename and store it in VPGNet """
        self.filename = filename
        self.img = caffe.io.load_image(filename)
        transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})
        transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost dimension
        transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
        transformer.set_channel_swap('data', (2, 1, 0))
        transformed_img = transformer.preprocess('data', self.img) # swap R, B channel, the final input to the network should be RGB
        self.net.blobs['data'].data[...] = transformed_img

    def forward(self):
        """ forward-propagation """
        self.net.forward()

    def extract_mask(self):
        """
        get the result from VPGNet
        the result is a binary mask, the mask is smaller than original picture because it is shrinked by grid_size
        """
        obj_mask = self.net.blobs['binary-mask'].data
        x_offset_mask = 4 # offset to align output with original pic: due to padding
        y_offset_mask = 4
        masked_img = self.img.copy()
        mask_grid_size = self.img.shape[0] / obj_mask.shape[2]
        small_mask = obj_mask[0, 1, ...] * 255
        self.resized_mask = cv2.resize(small_mask, (640, 480))
        translationM = np.float32([[1, 0, x_offset_mask*mask_grid_size], [0, 1, y_offset_mask*mask_grid_size]])
        self.resized_mask = cv2.warpAffine(self.resized_mask, translationM, (640, 480)) # translate (shift) the image
        # cv2.imwrite(workspace_root + 'mask.png', resized_mask)
        # return self.resized_mask

    def post_process(self, t1):
        """
        do post-processing of the mask and extract actual polylines out of it

        t: time spent on post-processing
        lines: polyline, format see lane_extension_polyline_for_VPG.py
        """
        self.t, self.lines_in_gnd, self.lines_in_img = pp.work(self.resized_mask, do_adjust=True, 
                                                               suppress_output=True, time1=t1, time2=t1)
        return self.t

    def visualize(self, num):
        """
        visualize the result of post-processing on the original picture

        num: the index of the picture being processed
        the output is stored in VPG_log/
        """
        original_img = cv2.imread(self.filename)
        original_img = cv2.resize(original_img, (640, 480))
        for line in self.lines_in_img:
            for i in range(len(line) - 1):
                cv2.line(original_img, (line[i][0], line[i][1]), (line[i+1][0], line[i+1][1]), (0, 0, 255), 5)
        cv2.imwrite('VPG_log/labeled/%d_labeled.png'%num, original_img)


def main():
    workspace_root = 'VPG_log/'
    detector = LaneDetector(workspace_root)
    t_sum = 0
    t_pp = 0
    t_net = 0
    for i in range(245):
        detector.load_image('../../cordova1/f'+str(i).zfill(5)+'.png')
        t0 = time.time()
        detector.forward()
        mask = detector.extract_mask()
        t1 = time.time()
        t = detector.post_process(t1)
        t_pp += t
        t_sum += time.time() - t0
        t_net += t1 - t0
        detector.visualize(i)
        # os.system('mv output_log/threshold.png VPG_log/log/%d.png'%i)
        # os.system('mv output_log/o.png VPG_log/log/%d_raw.png'%i)
    print 'total time ', t_sum / 245.0
    print 'VPGNet time ', t_net / 245.0
    print 'post-processing time ', t_pp / 245.0

if __name__ == '__main__':
    main()