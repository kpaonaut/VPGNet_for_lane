# This file is a different version of data_aug.py
# it is only used to generate flipped images for codova1
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
            # combined_labels.write(line) # comment this line so there is only g
            combined_labels.write('/' + category + '/g' + words[0][len(words[0]) - 9 : len(words[0])]) # picture name
            combined_labels.write('  ' + words[1]) # number of boxes
            while i < len(words) - 3:
                x_max = 639 - int(words[i])
                x_min = 639 - int(words[i + 2])
                combined_labels.write('  ' + str(x_min) + ' ' + words[i + 1] + ' ' + str(x_max) + ' ' + words[i + 3] + ' ' + words[i + 4])
                i += 5
            combined_labels.write('\n')
        f.close()
    combined_labels.close()
