import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
# from evaluate.lane import LaneEval
# %matplotlib inline

# class tusimpe_data:

def add_box(x, y, gg, gb):
    grid_box_x = (x - 1) // gg
    grid_box_y = (y - 1) // gg
    x_min = grid_box_x * gg
    x_max = grid_box_x * gg + gg
    y_min = grid_box_y * gg
    y_max = grid_box_y * gg + gg
    gb.append([x_min, y_min, x_max, y_max, 1]) # all lanes are classified as type 1

def main():

    mode = "annotate"
    if mode == "show_image":
        num = 1
        json_gt = [json.loads(line) for line in open('train_set/label_data_0313.json')]
        gt = json_gt[num]
        gt_lanes = gt['lanes']
        y_samples = gt['h_samples']
        raw_file = gt['raw_file']

        img = plt.imread('train_set/' + raw_file)
        # plt.imshow(img)
        # plt.show()

        gt_lanes_vis  = [[(x, y) for (x, y) in zip(lane, y_samples) if x >= 0] for lane in gt_lanes]
        img_vis = img.copy()

        for lane in gt_lanes_vis:
            for i in range(len(lane) - 1):
                pt1 = lane[i]
                pt2 = lane[i + 1]
                cv2.line(img_vis, pt1, pt2, (255, 0, 0))
                cv2.circle(img_vis, pt1, radius=5, color=(0, 255, 0))

        plt.imshow(img_vis)
        plt.show()

    json_gt = []
    tot = 0
    gg = 8
    thickness = 1
    label_file = open('./label_data_0313.txt', 'w')

    for line in open('train_set/label_data_0313.json'): # each line is a picture file

        gb = []
        json_gt.append(json.loads(line))
        tot += 1
        gt = json_gt[tot - 1]
        gt_lanes = gt['lanes']
        y_samples = gt['h_samples']
        raw_file = gt['raw_file']
        gt_lanes_vis  = [[(x, y) for (x, y) in zip(lane, y_samples) if x >= 0] for lane in gt_lanes]
        for each_lane in gt_lanes_vis:
            for (x, y) in each_lane:
                x_l = x - thickness
                x_r = x + thickness
                add_box(x, y, gg, gb)
                add_box(x_l, y, gg, gb)
                add_box(x_r, y, gg, gb)
        gb = np.array(gb)
        gb = np.unique(gb, axis = 0)

        label_file.write(raw_file + ' ' + str(gb.shape[0]))
        for box in gb:
            label_file.write(' ')
            label_file.write(' ' + str(box[0]) + ' ' + str(box[1]) + ' ' + str(box[2]) + ' ' + str(box[3]) + ' ' + str(box[4]))
        label_file.write('\n')

    label_file.close()


if __name__ == "__main__":
    main()