import cv2
import numpy as np
import os
import string

stage = 'label' # either label or image

categories = ['cordova1', 'cordova2', 'washington2']

if stage == 'image':
    # flip all the pix
    for category in categories:
        orig_images = os.listdir('../train/'+category)
        for img_dir in orig_images:
            if img_dir[0] == 'f' and img_dir[len(img_dir) - 3 : len(img_dir)] == 'png':
                img = cv2.imread('../train/'+category+'/' + img_dir)
                img = cv2.flip(img, 1)
                cv2.imwrite('../train/'+category+'/' + 'g' + img_dir[1 : len(img_dir)], img)

if stage == 'label':
    # label all flipped pix
    combined_labels = open('../train/combined_labels.txt', 'w')
    for category in categories:
        label = '../'+category+'.txt'
        f = open(label, 'r')
        for line in f:
            words = line.split()
            if words[0] in ['/cordova1/f00086.png', '/cordova2/f00046.png', '/washington2/f00054.png']: # 3 images reserved for test
                continue
            i = 2
            combined_labels.write(line)
            combined_labels.write('/' + category + '/g' + words[0][len(words[0]) - 9 : len(words[0])]) # picture name
            combined_labels.write(' ' + words[1]) # number of boxes
            box_list = []
            while i < len(words) - 3:
                x_max = 639 - int(words[i])
                y_max = int(words[i + 3])
                x_min = 639 - int(words[i + 2])
                y_min = int(words[i + 1])
                box_type = int(words[i + 4])
                box_list.append((x_min, y_min, x_max, y_max, box_type))
                # combined_labels.write('  ' + str(x_min) + ' ' + words[i + 1] + ' ' + str(x_max) + ' ' + words[i + 3] + ' ' + words[i + 4])
                i += 5
            box_list.sort(key = (lambda (a, b, c, d, e): a*1000000 + b * 1000 + c))
            for box in box_list:
                combined_labels.write(' ' + str(box[0]) + ' ' + str(box[1]) + ' ' + str(box[2]) + ' ' + str(box[3]) + ' ' + str(box[4]) )
            combined_labels.write('\n')
        f.close()
    combined_labels.close()
