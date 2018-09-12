import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time # time the execution time

import caffe
import cv2


class LaneDetector:
    """ The class which includes the entire pipeline of
    lane detection
    """

    def __init__(self, workspace_root='.'):
        if not os.path.exists(os.path.join(os.getcwd(), workspace_root)):
            os.mkdir(workspace_root)

        #self.model = '/home/rui/VPGNet/caffe/models/vpgnet-novp/deploy_Rui.prototxt' # deploy_Rui: pruned useless branches
        self.model = '/home/rui/VPGNet/caffe/models/vpgnet-novp/deploy.prototxt' # original deploy, no pruning
        self.pretrained = '/home/rui/VPGNet/caffe/models/vpgnet-novp/snapshots/split_iter_50000.caffemodel'
        caffe.set_mode_gpu()
        caffe.set_device(0)
        self.net = caffe.Net(self.model, self.pretrained, caffe.TEST)

    def load_image(self, filename):
        self.img = caffe.io.load_image(filename)
        transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})
        transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost dimension
        transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
        transformer.set_channel_swap('data', (2, 1, 0))
        transformed_img = transformer.preprocess('data', self.img) # swap R, B channel, the final input to the network should be RGB
        self.net.blobs['data'].data[...] = transformed_img

    def forward(self):
        self.net.forward()

    def extract_mask(self):
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
        return self.resized_mask


def main():
    detector = LaneDetector('VPG_log/')
    detector.load_image('example.png')
    detector.forward()
    mask = detector.extract_mask()
    # cv2.imwrite('workspace/4/mask.png', mask) # debug
    import lane_extension_polyline_for_VPG as pp
    time_tmp = time.time()
    pp.work(mask, do_adjust=True, suppress_output=False, time1=time_tmp, time2=time_tmp)

if __name__ == '__main__':
    main()